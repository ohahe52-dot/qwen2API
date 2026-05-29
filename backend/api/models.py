from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.core.config import MODEL_MAP, resolve_model
from backend.services.auth_quota import resolve_auth_context
from backend.services.qwen_client import QwenClient

router = APIRouter()


def _build_model_list_payload() -> dict:
    seen: set[str] = set()
    data: list[dict] = []

    # Những model quan trọng muốn hiện bản mode riêng
    suffix_models = ["qwen3.7-max", "qwen3.6-plus"]

    for model_id in MODEL_MAP:
        if model_id in seen:
            continue
        seen.add(model_id)
        data.append({"id": model_id, "object": "model", "owned_by": "qwen2api"})

        # Tự động thêm các bản mode cho model chính
        if model_id in suffix_models:
            for suffix in ["-fast", "-think"]:
                sid = f"{model_id}{suffix}"
                if sid not in seen:
                    seen.add(sid)
                    data.append({"id": sid, "object": "model", "owned_by": "qwen2api"})

    return {"object": "list", "data": data}


@router.get("/v1/models")
async def list_models(request: Request):
    app = request.app
    users_db = app.state.users_db
    client: QwenClient = app.state.qwen_client

    # 鉴权
    await resolve_auth_context(request, users_db)

    # Từ Account Pool lấy danh sách thực tế
    upstream_models = await client.list_models_from_pool()

    # Khởi tạo danh sách kết quả
    data = []
    seen = set()

    # Những model gốc quan trọng muốn tạo bản mode riêng
    suffix_bases = ["qwen3.7-max", "qwen3.6-plus", "qwen3.6-max-preview", "qwen3.5-plus", "qwen3.5-flash"]

    # 1. Ưu tiên các Alias từ MODEL_MAP (đã dọn dẹp)
    for alias_id in MODEL_MAP:
        if alias_id not in seen:
            seen.add(alias_id)
            data.append({"id": alias_id, "object": "model", "owned_by": "qwen2api"})

    # 2. Xử lý danh sách từ thượng nguồn (Upstream)
    if upstream_models:
        for item in upstream_models:
            if not isinstance(item, dict): continue
            mid = item.get("id") or item.get("model") or item.get("name")
            if not mid: continue

            # Lọc: Chỉ giữ lại những model chứa chữ "qwen"
            if "qwen" not in mid.lower(): continue

            # Nếu chưa có trong danh sách thì thêm vào
            if mid not in seen:
                seen.add(mid)
                data.append({
                    "id": mid,
                    "object": "model",
                    "owned_by": item.get("owned_by", "qwen"),
                    "created": item.get("created_at") or 0,
                })

    # 3. Tự động tiêm các bản mode (-fast, -think) cho các model quan trọng
    final_data = []
    for item in data:
        final_data.append(item)
        mid = item["id"]
        # Chỉ tiêm cho các model gốc, không tiêm cho Alias hoặc bản đã có hậu tố
        if mid in suffix_bases:
            for suffix in ["-fast", "-think"]:
                sid = f"{mid}{suffix}"
                if sid not in seen:
                    seen.add(sid)
                    final_data.append({"id": sid, "object": "model", "owned_by": "qwen2api"})

    return JSONResponse({"object": "list", "data": final_data})


@router.get("/v1/models/{model_id}")
async def get_model(model_id: str):
    resolved = resolve_model(model_id)
    if resolved == model_id and model_id not in MODEL_MAP:
        raise HTTPException(status_code=404, detail={"error": {"message": f"Model '{model_id}' not found", "type": "invalid_request_error"}})
    return JSONResponse({"id": model_id, "object": "model", "owned_by": "qwen2api", "resolved_model": resolved})
