import os
import json
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Dict, Set

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    # 服务配置
    PORT: int = int(os.getenv("PORT", 8080))
    WORKERS: int = int(os.getenv("WORKERS", 3))
    ADMIN_KEY: str = os.getenv("ADMIN_KEY", "admin")

    # 并发配置（浏览器仅用于账号注册，不用于对话请求）
    BROWSER_POOL_SIZE: int = int(os.getenv("BROWSER_POOL_SIZE", 1))
    MAX_INFLIGHT_PER_ACCOUNT: int = int(os.getenv("MAX_INFLIGHT", 2))
    BROWSER_STREAM_TIMEOUT_SECONDS: int = int(os.getenv("BROWSER_STREAM_TIMEOUT_SECONDS", 1800))

    # 容灾与限流
    MAX_RETRIES: int = 3
    RATE_LIMIT_COOLDOWN: int = 600
    ACCOUNT_MIN_INTERVAL_MS: int = int(os.getenv("ACCOUNT_MIN_INTERVAL_MS", 0))
    REQUEST_JITTER_MIN_MS: int = int(os.getenv("REQUEST_JITTER_MIN_MS", 0))
    REQUEST_JITTER_MAX_MS: int = int(os.getenv("REQUEST_JITTER_MAX_MS", 0))
    RATE_LIMIT_BASE_COOLDOWN: int = int(os.getenv("RATE_LIMIT_BASE_COOLDOWN", 600))
    RATE_LIMIT_MAX_COOLDOWN: int = int(os.getenv("RATE_LIMIT_MAX_COOLDOWN", 3600))

    # 日志
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 数据文件路径
    ACCOUNTS_FILE: str = os.getenv("ACCOUNTS_FILE", str(DATA_DIR / "accounts.json"))
    USERS_FILE: str = os.getenv("USERS_FILE", str(DATA_DIR / "users.json"))
    CAPTURES_FILE: str = os.getenv("CAPTURES_FILE", str(DATA_DIR / "captures.json"))
    CONFIG_FILE: str = os.getenv("CONFIG_FILE", str(DATA_DIR / "config.json"))

    # ????? / ????
    CONTEXT_INLINE_MAX_CHARS: int = int(os.getenv("CONTEXT_INLINE_MAX_CHARS", 4000))
    CONTEXT_FORCE_FILE_MAX_CHARS: int = int(os.getenv("CONTEXT_FORCE_FILE_MAX_CHARS", 10000))
    CONTEXT_ATTACHMENT_TTL_SECONDS: int = int(os.getenv("CONTEXT_ATTACHMENT_TTL_SECONDS", 1800))
    CONTEXT_UPLOAD_PARSE_TIMEOUT_SECONDS: int = int(os.getenv("CONTEXT_UPLOAD_PARSE_TIMEOUT_SECONDS", 60))
    CONTEXT_GENERATED_DIR: str = os.getenv("CONTEXT_GENERATED_DIR", str(DATA_DIR / "context_files"))
    CONTEXT_CACHE_FILE: str = os.getenv("CONTEXT_CACHE_FILE", str(DATA_DIR / "context_cache.json"))
    UPLOADED_FILES_FILE: str = os.getenv("UPLOADED_FILES_FILE", str(DATA_DIR / "uploaded_files.json"))
    CONTEXT_AFFINITY_FILE: str = os.getenv("CONTEXT_AFFINITY_FILE", str(DATA_DIR / "session_affinity.json"))
    CONTEXT_ALLOWED_GENERATED_EXTS: str = os.getenv("CONTEXT_ALLOWED_GENERATED_EXTS", "txt,md,json,log")
    CONTEXT_ALLOWED_USER_EXTS: str = os.getenv("CONTEXT_ALLOWED_USER_EXTS", "txt,md,json,log,xml,yaml,yml,csv,html,css,py,js,ts,java,c,cpp,cs,php,go,rb,sh,zsh,ps1,bat,cmd,pdf,doc,docx,ppt,pptx,xls,xlsx,png,jpg,jpeg,webp,gif,tiff,bmp,svg")

    class Config:
        env_file = ".env"

API_KEYS_FILE = DATA_DIR / "api_keys.json"

def load_api_keys() -> set:
    if API_KEYS_FILE.exists():
        try:
            with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data.get("keys", []))
        except Exception:
            pass
    return set()

def save_api_keys(keys: set):
    API_KEYS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(API_KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump({"keys": list(keys)}, f, indent=2)

# 在内存中存储管理的 API Keys
API_KEYS = load_api_keys()

VERSION = "2.0.0"

settings = Settings()

# 全局映射
MODEL_MAP = {
    # Qwen 3.7 Series
    "qwen3.7-max":          "qwen3.7-max",
    "qwen-max":             "qwen3.7-max",

    # Qwen 3.6 Series
    "qwen3.6-plus":         "qwen3.6-plus",
    "qwen-plus":            "qwen3.6-plus",
    "qwen":                 "qwen3.6-plus",

    # Qwen 3.5 Series
    "qwen3.5-plus":         "qwen3.5-plus",
    "qwen3.5-flash":        "qwen3.5-flash",
    "qwen-turbo":           "qwen3.5-flash",
}

def resolve_model(name: str) -> str:
    """
    解析模型 ID，支持带 hậu tố (-fast, -think, -auto).
    Nếu tìm thấy hậu tố, nó sẽ giải quyết phần tên gốc trước.
    """
    clean_name = name
    if name.endswith(("-fast", "-think", "-auto")):
        if name.endswith("-fast"): clean_name = name[:-5]
        elif name.endswith("-think"): clean_name = name[:-6]
        elif name.endswith("-auto"): clean_name = name[:-5]

    return MODEL_MAP.get(clean_name, clean_name)

def resolve_model_info(name: str) -> dict:
    """
    解析模型 ID 和思维模式。
    支持后缀: -fast (Fast), -think (Think), -auto (Auto)
    """
    mode = "Auto"
    clean_name = name

    if name.endswith("-fast"):
        mode = "Fast"
        clean_name = name[:-5]
    elif name.endswith("-think"):
        mode = "Think"
        clean_name = name[:-6]
    elif name.endswith("-auto"):
        mode = "Auto"
        clean_name = name[:-5]

    resolved = resolve_model(clean_name)
    return {
        "model": resolved,
        "thinking_mode": mode
    }
