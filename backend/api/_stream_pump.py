"""asyncio.Queue-based stream pump — chung cho OpenAI và Anthropic.

Mô phỏng pattern đã chạy ổn định trong gemini.py:
  - runner chạy collect_completion_run trong background task
  - on_delta → queue.put(chunk) → stream real-time
  - vòng lặp pump: queue.get() → yield ngay ra client
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

log = logging.getLogger("qwen2api.stream_pump")

# Types cho callback on_delta
DeltaCallback = Callable[[dict[str, Any], str | None, list[dict[str, Any]] | None], Awaitable[None]]

# Sentinel value để báo hiệu runner kết thúc
_SENTINEL = object()


class StreamPump:
    """Pump stream SSE chunks qua asyncio.Queue.

    Usage:
        pump = StreamPump()
        task = pump.start(runner_coro)
        async for chunk in pump.pump():
            yield chunk
        await task
    """

    def __init__(self):
        self.queue: asyncio.Queue[Any] = asyncio.Queue()
        self._task: asyncio.Task | None = None

    async def _run_with_guard(self, coro: Awaitable) -> None:
        """Chạy runner coroutine, bắt lỗi và gửi sentinel khi xong."""
        try:
            await coro
        except Exception as e:
            log.error("[StreamPump] runner lỗi: %s", e, exc_info=True)
            await self.queue.put(("error", e))
        finally:
            await self.queue.put(_SENTINEL)

    def start(self, coro: Awaitable) -> asyncio.Task:
        """Khởi chạy runner coroutine trong background task."""
        self._task = asyncio.create_task(self._run_with_guard(coro))
        return self._task

    async def pump(self):
        """Yield từng chunk từ queue cho đến khi gặp sentinel.

        Yield tuple: ("ok", chunk_string) hoặc ("error", Exception)
        """
        while True:
            item = await self.queue.get()
            if item is _SENTINEL:
                return
            yield item

    async def put(self, item: Any) -> None:
        """Đẩy một chunk vào queue (dùng trong on_delta)."""
        await self.queue.put(item)

    @property
    def task(self) -> asyncio.Task | None:
        return self._task


def make_on_delta(
    pump: StreamPump,
    *,
    streamer=None,  # IncrementalTextStreamer | None
    format_answer: Callable[[str], str] | None = None,
    format_reasoning: Callable[[str], str] | None = None,
    format_tool_calls: Callable[[list[dict]], str] | None = None,
) -> DeltaCallback:
    """Tạo callback on_delta đẩy SSE chunks vào pump queue.

    Args:
        pump: StreamPump instance
        streamer: IncrementalTextStreamer để guard tool-call text (nếu có)
        format_answer: Hàm format text answer → SSE chunk string
        format_reasoning: Hàm format reasoning text → SSE chunk string
        format_tool_calls: Hàm format tool_calls list → SSE chunk string

    Returns:
        async on_delta(evt, text_chunk, tool_calls)
    """

    async def _on_delta(
        evt: dict[str, Any],
        text_chunk: str | None,
        tool_calls: list[dict[str, Any]] | None,
    ) -> None:
        phase = evt.get("phase", "")

        # Reasoning / thinking: stream ngay không qua guard
        if text_chunk and phase in ("think", "thinking_summary"):
            if format_reasoning:
                await pump.put(("ok", format_reasoning(text_chunk)))
            return

        # Answer text: qua streamer guard (nếu có)
        if text_chunk and phase == "answer":
            if streamer is not None and format_answer:
                released = streamer.push(text_chunk)
                if released:
                    await pump.put(("ok", format_answer(released)))
            elif format_answer:
                # Không có streamer → stream ngay (chế độ không tools)
                await pump.put(("ok", format_answer(text_chunk)))
            return

        # Tool calls: stream ngay
        if tool_calls and format_tool_calls:
            await pump.put(("ok", format_tool_calls(tool_calls)))
            return

    return _on_delta


def flush_streamer_tail(
    streamer,
    format_answer: Callable[[str], str] | None = None,
) -> list[str]:
    """Flush phần còn lại của streamer (sau khi runner kết thúc).

    Returns danh sách SSE chunk strings cần yield sau pump loop.
    """
    if streamer is None or format_answer is None:
        return []
    tail = streamer.finish()
    if tail:
        return [format_answer(tail)]
    return []
