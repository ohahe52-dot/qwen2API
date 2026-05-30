from __future__ import annotations

import asyncio
import json
from typing import Any, Callable

from backend.adapter.standard_request import CLAUDE_CODE_OPENAI_PROFILE, OPENCLAW_OPENAI_PROFILE
from backend.runtime.execution import RuntimeToolDirective
from backend.toolcall.parser import parse_tool_calls_detailed


STRICT_TOOL_TEXT_PREFIXES = ("{", "[", "`", "<", "#")
BUFFERED_TOOL_CALLS_ONLY = "buffered_tool_calls_only"
DIRECTIVE_DRIVEN_TOOL_CALLS = "directive_driven_tool_calls"


class OpenAIStreamTranslator:
    def __init__(
        self,
        *,
        completion_id: str,
        created: int,
        model_name: str,
        client_profile: str,
        build_final_directive: Callable[[str], RuntimeToolDirective] | None = None,
        allowed_tool_names: list[str] | None = None,
        stream_callback: Callable[[str], None] | None = None,
    ):
        self.completion_id = completion_id
        self.created = created
        self.model_name = model_name
        self.client_profile = client_profile
        self.build_final_directive = build_final_directive
        self.allowed_tool_names = {name for name in (allowed_tool_names or []) if isinstance(name, str) and name}
        self.stream_callback = stream_callback  # Nếu set → emit chunks real-time
        self.pending_chunks: list[str] = []
        self.role_chunk_sent = False
        self.emitted_tool_index = 0
        self.answer_fragments: list[str] = []
        self.buffered_toolish_fragments: list[str] = []
        self.pending_content_chunks: list[str] = []
        self.tool_calls_emitted = False
        self._finalizing = False  # flag: đang trong finalize, không emit qua callback
        self.tool_text_detection_mode = self._resolve_tool_text_detection_mode(client_profile)
        self.tool_call_finalize_mode = self._resolve_tool_call_finalize_mode(client_profile)
        self._buffering_tool = False  # track: đang buffer tool content (một khi bắt đầu thì không dừng)
        self.content_accumulator = ""  # tích lũy text content để lọc marker không bị rò rỉ khi stream bị phân mảnh

    @staticmethod
    def _resolve_tool_text_detection_mode(client_profile: str) -> str:
        if client_profile == OPENCLAW_OPENAI_PROFILE:
            return "strict_prefix"
        return "accept_any_tool_syntax"

    @staticmethod
    def _resolve_tool_call_finalize_mode(client_profile: str) -> str:
        # Use directive-driven for all profiles: always try to parse tool calls from
        # answer_fragments via build_final_directive, rather than requiring buffered content.
        # This fixes CLAUDE_CODE profile where ##TOOL_CALL## markers were previously dropped.
        return DIRECTIVE_DRIVEN_TOOL_CALLS

    @staticmethod
    def _find_partial_marker_length(text: str, markers: list[str]) -> int:
        if not text:
            return 0
        text_lower = text.lower()
        for i in range(min(len(text), 30), 0, -1):
            suffix = text_lower[-i:]
            for m in markers:
                if m.startswith(suffix) and len(suffix) < len(m):
                    return len(suffix)
        return 0

    def _looks_like_tool_output(self, text_chunk: str) -> bool:
        if not text_chunk:
            return False
        lowered = text_chunk.lower()

        # Once we've started buffering tool content, keep buffering everything
        # (tool calls can span many chunks; we don't want to emit partial markers as content)
        if self._buffering_tool:
            return True

        # Fast path: detect partial ##TOOL_CALL## markers even in small chunks
        if any(marker in lowered for marker in ("##tool_call", "##end_call")):
            self._buffering_tool = True
            return True

        # Common refusal/toxic markers that indicate tool output
        common_markers = (
            "tool does not exists",
            "</think>",
            "function.name:",
            '"tool_calls"',
            '"function":',
        )
        if any(marker in lowered for marker in common_markers):
            return True

        if self.allowed_tool_names:
            detailed = parse_tool_calls_detailed(text_chunk, self.allowed_tool_names)
            if detailed.get("saw_tool_syntax"):
                if self.tool_text_detection_mode == "strict_prefix":
                    stripped = text_chunk.lstrip()
                    return stripped.startswith(STRICT_TOOL_TEXT_PREFIXES)
                return True
        return False

    def _should_finalize_tool_calls(self, directive: RuntimeToolDirective) -> bool:
        if directive.stop_reason != "tool_use":
            return False
        if self.tool_call_finalize_mode == BUFFERED_TOOL_CALLS_ONLY:
            return bool(self.buffered_toolish_fragments)
        return True

    def _make_chunk(self, delta: dict, finish_reason=None) -> str:
        payload = {
            "id": self.completion_id,
            "object": "chat.completion.chunk",
            "created": self.created,
            "model": self.model_name,
            "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
        }
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def _ensure_role_chunk(self) -> None:
        if self.role_chunk_sent:
            return
        chunk = self._make_chunk({"role": "assistant"})
        if self.stream_callback:
            if asyncio.iscoroutinefunction(self.stream_callback):
                await self.stream_callback(chunk)
            else:
                self.stream_callback(chunk)
        else:
            self.pending_chunks.append(chunk)
        self.role_chunk_sent = True

    async def _emit_content_chunk(self, text_chunk: str) -> None:
        chunk = self._make_chunk({"content": text_chunk})
        if self.stream_callback and not self._finalizing:
            if asyncio.iscoroutinefunction(self.stream_callback):
                await self.stream_callback(chunk)
            else:
                self.stream_callback(chunk)
        else:
            self.pending_chunks.append(chunk)
            if not self._finalizing:
                self.pending_content_chunks.append(chunk)

    async def _emit_reasoning_chunk(self, text_chunk: str) -> None:
        chunk = self._make_chunk({"reasoning_content": text_chunk})
        if self.stream_callback:
            if asyncio.iscoroutinefunction(self.stream_callback):
                await self.stream_callback(chunk)
            else:
                self.stream_callback(chunk)
        else:
            self.pending_chunks.append(chunk)

    def _discard_pending_content_chunks(self) -> None:
        if not self.pending_content_chunks:
            return
        pending_content_ids = {id(chunk) for chunk in self.pending_content_chunks}
        self.pending_chunks = [chunk for chunk in self.pending_chunks if id(chunk) not in pending_content_ids]
        self.pending_content_chunks = []

    async def on_delta(self, evt: dict[str, Any], text_chunk: str | None, tool_calls: list[dict[str, Any]] | None) -> None:
        await self._ensure_role_chunk()

        if text_chunk and evt.get("phase") in ("think", "thinking_summary"):
            await self._emit_reasoning_chunk(text_chunk)
            return

        if text_chunk and evt.get("phase") == "answer":
            self.answer_fragments.append(text_chunk)

            if self._buffering_tool:
                self.buffered_toolish_fragments.append(text_chunk)
                return

            self.content_accumulator += text_chunk

            # Các marker hoàn chỉnh biểu thị sự bắt đầu của một công cụ gọi
            markers = [
                "##tool_call##",
                "<tool_call>",
                '{"tool_calls"',
                '{"name":',
                "function.name:",
                '"tool_calls"',
                '"function":',
                "tool does not exists",
                "</think>"
            ]

            # Tìm xem có marker hoàn chỉnh nào bắt đầu xuất hiện trong bộ đệm tích lũy
            found_marker_idx = -1
            lower_accum = self.content_accumulator.lower()
            for m in markers:
                idx = lower_accum.find(m)
                if idx >= 0:
                    if found_marker_idx == -1 or idx < found_marker_idx:
                        found_marker_idx = idx

            if found_marker_idx >= 0:
                # Giải phóng phần text an toàn nằm trước marker gọi tool
                safe_text = self.content_accumulator[:found_marker_idx]
                if safe_text:
                    await self._emit_content_chunk(safe_text)

                # Bắt đầu đưa phần marker gọi tool và phần phía sau vào bộ đệm tool
                tool_text = self.content_accumulator[found_marker_idx:]
                self.buffered_toolish_fragments.append(tool_text)
                self._buffering_tool = True
                self.content_accumulator = ""
                return

            # Nếu chưa có marker hoàn chỉnh, kiểm tra xem phần đuôi có phải là một marker dở dang (partial) hay không
            partial_len = self._find_partial_marker_length(self.content_accumulator, markers)
            if partial_len > 0:
                # Giải phóng phần text an toàn, giữ lại đuôi dở dang để gộp tiếp ở chunk sau
                safe_text = self.content_accumulator[:-partial_len]
                if safe_text:
                    await self._emit_content_chunk(safe_text)
                self.content_accumulator = self.content_accumulator[-partial_len:]
            else:
                # Không có marker dở dang, giải phóng toàn bộ bộ đệm tích lũy an toàn ra client
                await self._emit_content_chunk(self.content_accumulator)
                self.content_accumulator = ""
            return

        if tool_calls:
            await self.emit_tool_calls(tool_calls)

    async def emit_tool_calls(self, tool_calls: list[dict[str, Any]]) -> None:
        await self._ensure_role_chunk()
        for tool_call in tool_calls:
            idx = self.emitted_tool_index
            self.emitted_tool_index += 1
            chunk = self._make_chunk({
                "tool_calls": [{
                    "index": idx,
                    "id": tool_call["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call["name"],
                        "arguments": json.dumps(tool_call["input"], ensure_ascii=False),
                    },
                }],
            })
            if self.stream_callback and not self._finalizing:
                if asyncio.iscoroutinefunction(self.stream_callback):
                    await self.stream_callback(chunk)
                else:
                    self.stream_callback(chunk)
            else:
                self.pending_chunks.append(chunk)
        if tool_calls:
            self.tool_calls_emitted = True

    async def finalize(self, finish_reason: str) -> list[str]:
        final_finish_reason = finish_reason
        self._finalizing = True  # ngăn emit_content_chunk callback vào pump đã đóng

        # Flush bất kỳ nội dung nào còn dư lại trong bộ tích lũy ra các kênh tương ứng trước khi đóng
        if self.content_accumulator:
            if self._buffering_tool:
                self.buffered_toolish_fragments.append(self.content_accumulator)
            else:
                await self._emit_content_chunk(self.content_accumulator)
            self.content_accumulator = ""

        buffered_text = "".join(self.buffered_toolish_fragments)
        if self.build_final_directive is not None and not self.tool_calls_emitted:
            directive = self.build_final_directive("".join(self.answer_fragments))
            if self._should_finalize_tool_calls(directive):
                self._discard_pending_content_chunks()
                tool_calls = [
                    {
                        "id": block["id"],
                        "name": block["name"],
                        "input": block.get("input", {}),
                    }
                    for block in directive.tool_blocks
                    if block.get("type") == "tool_use"
                ]
                if tool_calls:
                    await self.emit_tool_calls(tool_calls)
                    final_finish_reason = "tool_calls"
            elif buffered_text and not self.tool_calls_emitted:
                await self._emit_content_chunk(buffered_text)
        elif buffered_text and not self.tool_calls_emitted:
            await self._emit_content_chunk(buffered_text)

        # Trong stream mode, bất kỳ chunk nào chưa gửi (hoặc được tạo trong finalize như tool_calls)
        # phải được gom cùng finish + DONE để trả về trực tiếp từ hàm generator của v1_chat.py
        if self.stream_callback:
            finish_chunk = self._make_chunk({}, final_finish_reason)
            done = "data: [DONE]\n\n"
            return list(self.pending_chunks) + [finish_chunk, done]

        chunks = list(self.pending_chunks)
        chunks.append(self._make_chunk({}, final_finish_reason))
        chunks.append("data: [DONE]\n\n")
        return chunks
