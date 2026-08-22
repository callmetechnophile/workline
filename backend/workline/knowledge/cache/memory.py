"""Thread-safe L1 in-memory bounded LRU cache with TTL support."""

from collections import OrderedDict
import threading
import time
from typing import Any, Dict, List, Optional, Tuple
from backend.workline.knowledge.cache.models import CacheMetadata


class MemoryCache:
    """Bounded in-process memory cache using OrderedDict for LRU eviction."""

    def __init__(self, max_entries: int = 1500):
        self.max_entries = max_entries
        self._lock = threading.RLock()
        self._cache: OrderedDict[str, Tuple[CacheMetadata, Any]] = OrderedDict()

    def get(self, key: str) -> Optional[Tuple[CacheMetadata, Any]]:
        with self._lock:
            if key not in self._cache:
                return None

            meta, data = self._cache[key]
            # Check expiration
            if meta.expires_at > 0 and time.time() > meta.expires_at:
                del self._cache[key]
                return None

            # Move to end for LRU refresh
            self._cache.move_to_end(key)
            return meta, data

    def set(self, key: str, meta: CacheMetadata, data: Any) -> None:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self.max_entries:
                # Evict least recently used (first item)
                self._cache.popitem(last=False)

            self._cache[key] = (meta, data)

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        with self._lock:
            return len(self._cache)

    def clear_expired(self) -> int:
        with self._lock:
            now = time.time()
            expired_keys = [k for k, (meta, _) in self._cache.items() if meta.expires_at > 0 and now > meta.expires_at]
            for k in expired_keys:
                del self._cache[k]
            return len(expired_keys)

    def get_all_entries(self) -> List[Tuple[CacheMetadata, Any]]:
        with self._lock:
            return list(self._cache.values())
