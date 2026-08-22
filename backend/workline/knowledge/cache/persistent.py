"""Thread-safe L2 Persistent filesystem cache under .workline/cache/"""

import json
import os
import shutil
import threading
import time
from typing import Any, Dict, Optional, Tuple
from backend.workline.knowledge.cache.models import CacheMetadata, CacheObjectType


class PersistentCache:
    """Stores serialized JSON cache items in organized directories under .workline/cache/"""

    def __init__(self, base_dir: str = ".workline/cache"):
        self.base_dir = base_dir
        self._lock = threading.RLock()
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        try:
            subdirs = ["metadata", "documents", "embeddings", "retrieval", "context", "summaries"]
            for sub in subdirs:
                os.makedirs(os.path.join(self.base_dir, sub), exist_ok=True)
        except Exception:
            pass

    def _get_path(self, key: str, object_type: CacheObjectType) -> str:
        safe_key = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        folder = "metadata"
        if object_type in (CacheObjectType.DOCUMENT_PARSE, CacheObjectType.DOCUMENT_CHUNK):
            folder = "documents"
        elif object_type == CacheObjectType.EMBEDDING:
            folder = "embeddings"
        elif object_type == CacheObjectType.RETRIEVAL:
            folder = "retrieval"
        elif object_type == CacheObjectType.CONTEXT:
            folder = "context"
        elif object_type in (CacheObjectType.SUMMARY, CacheObjectType.RESEARCH):
            folder = "summaries"

        return os.path.join(self.base_dir, folder, f"{safe_key}.json")

    def get(self, key: str, object_type: CacheObjectType) -> Optional[Tuple[CacheMetadata, Any]]:
        with self._lock:
            path = self._get_path(key, object_type)
            if not os.path.exists(path):
                return None

            try:
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)

                meta = CacheMetadata.model_validate(payload["metadata"])
                data = payload["data"]

                # Check expiration
                if meta.expires_at > 0 and time.time() > meta.expires_at:
                    self.delete(key, object_type)
                    return None

                return meta, data
            except Exception:
                # Discard corrupted file
                self.delete(key, object_type)
                return None

    def set(self, key: str, meta: CacheMetadata, data: Any) -> None:
        with self._lock:
            path = self._get_path(key, meta.object_type)
            try:
                payload = {
                    "metadata": meta.model_dump(),
                    "data": data,
                }
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(payload, f, ensure_ascii=False)
            except Exception:
                pass

    def delete(self, key: str, object_type: CacheObjectType) -> bool:
        with self._lock:
            path = self._get_path(key, object_type)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    return True
                except Exception:
                    return False
            return False

    def clear(self) -> None:
        with self._lock:
            if os.path.exists(self.base_dir):
                try:
                    shutil.rmtree(self.base_dir)
                except Exception:
                    pass
            self._ensure_directories()

    def get_stats(self) -> Tuple[int, int]:
        """Returns (total_entries, total_size_bytes)."""
        with self._lock:
            total_entries = 0
            total_size = 0
            for root, _, files in os.walk(self.base_dir):
                for f in files:
                    if f.endswith(".json"):
                        total_entries += 1
                        try:
                            total_size += os.path.getsize(os.path.join(root, f))
                        except Exception:
                            pass
            return total_entries, total_size
