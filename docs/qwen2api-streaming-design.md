# Qwen2API Real-Time Streaming Design

## Problem Statement

OpenAI (`/v1/chat/completions`) và Anthropic (`/v1/messages`) endpoint hiện tại **buffer toàn bộ response rồi mới xả** qua `translator.finalize()` / `stream_state.pending_chunks` → client nhận tất cả cùng lúc, không có hiệu ứng typewriter như ds2apimod-vn. Chỉ Gemini endpoint là stream thật (dùng `asyncio.Queue`).

## Goal

Cả 3 endpoint (OpenAI, Anthropic, Gemini) đều stream từng chữ real-time qua SSE. Tool-call phải hoạt động đúng, không rò cú pháp `##TOOL_CALL##` ra client.

## Architecture

### Core Insight

Qwen upstream trả text theo **delta tăng dần** (mỗi chunk là 1 đoạn text mới, cần `"".join(answer_fragments)`). Tool-call được nhúng dưới dạng text marker `##TOOL_CALL##` trong phase `answer` — khi phát hiện, `collect_completion_run` finalize sớm (dòng 590, execution.py). Không có frame tool-call riêng như ds2apimod-vn.

### Design Decision: Guard Window

Mỗi text delta đi qua `IncrementalTextStreamer` (giữ lại 256 ký tự cuối) → text "an toàn" được bọc SSE chunk → `queue.put()` → generator `yield` ngay. Nếu phát hiện `##TOOL_CALL##` trong vùng guard, phần đuôi không xả ra client → không rò tool-call.

### New File: `backend/api/_stream_pump.py`

Helper chung đóng gói pattern `asyncio.Queue` + `create_task`, tái dùng cho cả OpenAI và Anthropic:

```python
class StreamPump:
    """asyncio.Queue-based pump: runner writes → loop reads → yields SSE chunks."""
    def __init__(self):
        self.queue = asyncio.Queue()

    async def runner(self, coro):
        try:
            await coro
        except Exception as e:
            await self.queue.put(("error", e))
        finally:
            await self.queue.put(("done", None))

    def start(self, coro):
        return asyncio.create_task(self.runner(coro))

    async def pump(self):
        while True:
            kind, payload = await self.queue.get()
            if kind == "error":
                yield f"data: {{\"error\": \"{payload}\"}}\n\n"
                return
            if kind == "done":
                return
            yield payload  # payload is already SSE-formatted string
```

### File Changes

#### 1. `backend/api/_stream_pump.py` (MỚI)
- Class `StreamPump` như trên
- Helper `pump_on_delta(queue, format_fn)` → trả về `async def on_delta(evt, text, tool_calls)` gọi `queue.put(format_fn(...))`

#### 2. `backend/api/v1_chat.py` (OpenAI) — refactor `generate()`
**Trước:** `on_delta` → `translator.pending_chunks.append()` → `finalize()` yield tất cả.
**Sau:**

```python
async def generate():
    pump = StreamPump()
    
    # Format chunk → SSE OpenAI format
    def openai_chunk(text):
        return f"data: {json.dumps({...delta: {content: text}...})}\n\n"

    async def on_delta(evt, text_chunk, tool_calls):
        # reasoning: stream ngay
        if evt.get("phase") in ("think", "thinking_summary") and text_chunk:
            await pump.queue.put(openai_reasoning_chunk(text_chunk))
        # answer: qua streamer để guard
        elif evt.get("phase") == "answer" and text_chunk:
            released = streamer.push(text_chunk)  # giữ 256 ký tự cuối
            if released:
                await pump.queue.put(openai_chunk(released))
        # tool_call: stream ngay
        elif tool_calls:
            await pump.queue.put(openai_tool_chunk(tool_calls))

    task = pump.start(run_with_recovery(on_delta=on_delta))
    
    # Pump SSE chunks real-time
    async for chunk in pump.pump():
        yield chunk
    
    # Runner kết thúc → flush streamer + finalize translator
    tail = streamer.finish()
    if tail:
        yield openai_chunk(tail)
    for chunk in translator.finalize(finish_reason):
        yield chunk
    await task
```

#### 3. `backend/api/anthropic.py` — refactor `generate()`
Tương tự OpenAI nhưng dùng `stream_presenter.anthropic_*` và `_AnthropicStreamState`:

```python
async def generate():
    pump = StreamPump()
    streamer = IncrementalTextStreamer(warmup_chars=64, guard_chars=256)
    stream_state = _AnthropicStreamState(...)

    async def on_delta(evt, text_chunk, _):
        # ... same pattern, stream_state.ensure_message_start()
        if evt.get("phase") == "answer" and text_chunk:
            released = streamer.push(text_chunk)
            if released:
                stream_state.buffer_answer_text(released)  # vẫn track cho finalize
                await pump.queue.put(stream_presenter.anthropic_content_block_delta(idx, {"type": "text", "text": released}))
        # ... reasoning, tool_call như cũ

    task = pump.start(collect_completion_run_with_recovery(..., on_delta=on_delta))
    
    async for chunk in pump.pump():
        yield chunk
    
    # Flush + finalize như cũ
    tail = streamer.finish()
    if tail:
        stream_state.buffer_answer_text(tail)
        yield stream_presenter.anthropic_content_block_delta(idx, {"type": "text", "text": tail})
    # ... stream_state.close_current_block(), flush_answer_text(), message_delta, message_stop
    for chunk in stream_state.pending_chunks:
        yield chunk
    await task
```

#### 4. `backend/services/incremental_text_streamer.py` — không đổi
Đã đủ tính năng (warmup + guard + finish). Chỉ cần bump `guard_chars` từ 96→256 trong Anthropic path.

### Retry Handling

**Vấn đề:** Khi stream real-time, nếu retry xảy ra sau khi đã có bytes ra client → client sẽ thấy nội dung từ lần retry cũ + lần mới → hiển thị sai.

**Giải pháp:**
1. OpenAI path hiện `allow_after_visible_output=True` → retry có thể xảy ra sau khi đã stream. **Giải pháp:** trong `generate()`, nếu `pump.pump()` phát hiện retry (`result.retry`), yield 1 error chunk với message "Retrying..." rồi tiếp tục stream attempt mới. Client tự xử lý (Claude Code, OpenClaw đều chịu được multiple message_start/role chunks).
2. Anthropic path tương tự — nhưng Anthropic protocol cho phép nhiều `content_block_start/stop` trong cùng message, nên retry tự nhiên hơn.
3. **Fallback an toàn:** nếu retry xảy ra và không thể tiếp tục stream (vd: đã stream >1000 chars), finalize attempt hiện tại + gửi `[DONE]`, rồi không retry nữa. Điều này ưu tiên consistency hơn retry rate.

### Tool-Call Safety

```
Qwen text: "Tôi sẽ dùng công cụ X\n##TOOL_CALL##\n{...}"
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                         IncrementalTextStreamer.guard = 256 chars

Nếu "##TOOL_CALL##" xuất hiện trong guard → không xả → finalize tool
Nếu "##TOOL_CALL##" không xuất hiện → guard window giải phóng text ra client
```

Khi `collect_completion_run` detect `##TOOL_CALL##` và finalize sớm:
1. `pump.pump()` nhận `("done", None)` → exit loop
2. `streamer.finish()` → trả về phần guard còn lại
3. **Không xả** phần guard nếu chứa marker → `translator.finalize("tool_calls")` thay thế
4. Client chỉ thấy text trước guard, không thấy `##TOOL_CALL##`

### Error Handling

| Tình huống | Xử lý |
|---|---|
| Upstream timeout | Runner ném exception → `pump` bắt → yield error chunk → `[DONE]` |
| Tool-call leak (guard fail) | `translator._looks_like_tool_output()` → discard pending content chunks |
| Retry after streaming | Nếu <1000 chars đã stream → tiếp tục attempt mới. Nếu ≥1000 → finalize, không retry |
| Queue full | Không giới hạn (asyncio.Queue không có maxsize) — an toàn vì runner slow hơn consumer |

### Testing Plan

1. **Unit test:** `IncrementalTextStreamer` — đẩy text chứa `##TOOL_CALL##` ở cuối, verify không leak
2. **Integration test:** Mock Qwen stream → pump → verify chunks yield đúng thứ tự
3. **Manual test:** Gọi `/v1/chat/completions` với `stream=true`, quan sát typewriter effect
4. **Tool-call test:** Request với tools, verify tool-call không rò ra client

### Files Modified Summary

| File | Action | Mô tả |
|---|---|---|
| `backend/api/_stream_pump.py` | **NEW** | StreamPump class + helper |
| `backend/api/v1_chat.py` | MODIFIED | Refactor `generate()` dùng pump |
| `backend/api/anthropic.py` | MODIFIED | Refactor `generate()` dùng pump |
| `backend/api/gemini.py` | NO CHANGE | Đã stream thật, không đổi |
| `backend/services/incremental_text_streamer.py` | NO CHANGE | Đã đủ tính năng |

### Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Tool-call marker leak qua guard | Guard 256 chars (đủ cho `##TOOL_CALL##` + JSON đầu) + `_looks_like_tool_output()` fallback |
| Retry sau khi stream dài | Cutoff 1000 chars → không retry nữa |
| Performance (Queue overhead) | Không đáng kể — Gemini đã chứng minh ổn định |
| Breaking change cho client | Không — format SSE không đổi, chỉ thay đổi timing |
