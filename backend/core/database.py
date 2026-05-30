import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("qwen2api.db")

class AsyncJsonDB:
    """带异步读写锁的 JSON 文件存储，防止并发损坏。"""
    def __init__(self, path: str | Path, default_data: Any = None):
        self.path = Path(path)
        self.default_data = default_data if default_data is not None else []
        self._lock = asyncio.Lock()
        self._data: Any = None
        self._init_file()

    def _init_file(self):
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.default_data, indent=2, ensure_ascii=False), encoding="utf-8")

    async def load(self) -> Any:
        async with self._lock:
            if not self.path.exists():
                self._data = self.default_data
                return self._data
            try:
                # 为了不阻塞事件循环，本应用可使用 asyncio.to_thread 或者直接读，因为文件很小
                content = self.path.read_text(encoding="utf-8")
                self._data = json.loads(content)
            except Exception as e:
                log.error(f"Failed to load JSON from {self.path}: {e}")
                self._data = self.default_data
            return self._data

    async def save(self, data: Any):
        async with self._lock:
            self._data = data
            try:
                self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
            except Exception as e:
                log.error(f"Failed to save JSON to {self.path}: {e}")

    async def get(self) -> Any:
        if self._data is None:
            return await self.load()
        return self._data

    async def update_one(
        self,
        match_field: str,
        match_value: Any,
        update_field: str,
        delta: Any,
        *,
        op: str = "add",
    ) -> bool:
        """Atomically update one record matching match_field == match_value.

        The entire read-modify-write happens under self._lock so concurrent
        callers cannot overwrite each other's changes.

        Supported ops: "add" (+=), "set" (=), "set_if_not_none".
        Returns True if a matching record was found and updated.
        """
        async with self._lock:
            data = await self._load_locked()
            if not isinstance(data, list):
                return False
            for item in data:
                if isinstance(item, dict) and item.get(match_field) == match_value:
                    if op == "add":
                        item[update_field] = item.get(update_field, 0) + delta
                    elif op == "set":
                        item[update_field] = delta
                    elif op == "set_if_not_none" and delta is not None:
                        item[update_field] = delta
                    else:
                        return False
                    await self._save_locked(data)
                    return True
            return False

    async def _load_locked(self) -> Any:
        """Load data under caller-held lock (internal helper)."""
        if self._data is not None:
            return self._data
        if not self.path.exists():
            self._data = self.default_data
        else:
            try:
                content = self.path.read_text(encoding="utf-8")
                self._data = json.loads(content)
            except Exception as e:
                log.error(f"Failed to load JSON from {self.path}: {e}")
                self._data = self.default_data
        return self._data

    async def _save_locked(self, data: Any) -> None:
        """Save data under caller-held lock (internal helper)."""
        self._data = data
        try:
            self.path.write_text(json.dumps(self._data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            log.error(f"Failed to save JSON to {self.path}: {e}")
