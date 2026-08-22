"""Central KnowledgeCache facade coordinating L1 Memory, L2 Persistent storage, and invalidation."""

import json
import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.knowledge.cache.invalidation import InvalidationManager
from backend.workline.knowledge.cache.memory import MemoryCache
from backend.workline.knowledge.cache.models import (
    CacheMetadata,
    CacheObjectType,
    CacheOptions,
    CacheStats,
)
from backend.workline.knowledge.cache.persistent import PersistentCache


class KnowledgeCache:
    """
    Two-tiered cache engine (L1 in-process memory + L2 persistent filesystem).
    Ensures non-authoritative caching, strict TTL, and project/team isolation.
    """

    def __init__(
        self,
        l1_max_entries: int = 2000,
        l2_base_dir: str = ".workline/cache",
    ):
        self.l1 = MemoryCache(l1_max_entries)
        self.l2 = PersistentCache(l2_base_dir)
        self.invalidation = InvalidationManager()
        self._lock = threading.RLock()
        self._stats = CacheStats()

    def get(self, key: str, object_type: CacheObjectType = CacheObjectType.RETRIEVAL) -> Optional[Any]:
        """Fetch item from L1 memory or fallback to L2 persistent cache."""
        with self._lock:
            # 1. Check L1 Memory
            l1_item = self.l1.get(key)
            if l1_item is not None:
                self._stats.hits += 1
                return l1_item[1]

            # 2. Check L2 Persistent
            l2_item = self.l2.get(key, object_type)
            if l2_item is not None:
                meta, data = l2_item
                # Promote to L1
                self.l1.set(key, meta, data)
                self._stats.hits += 1
                return data

            self._stats.misses += 1
            return None

    def set(
        self,
        key: str,
        value: Any,
        object_type: CacheObjectType,
        options: CacheOptions,
    ) -> None:
        """Store item into both L1 and L2 caches."""
        now = time.time()
        ttl_seconds = options.ttl if options.ttl is not None else self._get_default_ttl(object_type)
        expires_at = now + ttl_seconds if ttl_seconds > 0 else 0.0

        try:
            size_bytes = len(json.dumps(value, default=str))
        except Exception:
            size_bytes = 100

        meta = CacheMetadata(
            cache_key=key,
            object_type=object_type,
            project_id=options.project_id,
            team_id=options.team_id,
            source_id=options.source_id,
            source_hash=options.source_hash,
            schema_version=options.schema_version,
            created_at=now,
            expires_at=expires_at,
            project_version=options.project_version,
            git_commit=options.git_commit,
            provider=options.provider,
            model=options.model,
            embedding_dimension=options.embedding_dimension,
            size_bytes=size_bytes,
        )

        with self._lock:
            self.l1.set(key, meta, value)
            self.l2.set(key, meta, value)
            self.invalidation.track(key, options.project_id, options.source_id)

    def has(self, key: str, object_type: CacheObjectType = CacheObjectType.RETRIEVAL) -> bool:
        return self.get(key, object_type) is not None

    def delete(self, key: str, object_type: CacheObjectType = CacheObjectType.RETRIEVAL) -> bool:
        with self._lock:
            self.l1.delete(key)
            deleted_l2 = self.l2.delete(key, object_type)
            self.invalidation.remove_key(key)
            return deleted_l2

    def invalidate_by_source(self, source_id: str) -> int:
        with self._lock:
            keys = self.invalidation.get_keys_by_source(source_id)
            for k in keys:
                self.l1.delete(k)
                for t in CacheObjectType:
                    self.l2.delete(k, t)
            self._stats.invalidations += len(keys)
            return len(keys)

    def invalidate_by_project(self, project_id: str) -> int:
        with self._lock:
            keys = self.invalidation.get_keys_by_project(project_id)
            for k in keys:
                self.l1.delete(k)
                for t in CacheObjectType:
                    self.l2.delete(k, t)
            self._stats.invalidations += len(keys)
            return len(keys)

    def clear(self) -> None:
        with self._lock:
            self.l1.clear()
            self.l2.clear()
            self.invalidation.clear()

    def clear_expired(self) -> int:
        with self._lock:
            expired_l1 = self.l1.clear_expired()
            self._stats.expired += expired_l1
            return expired_l1

    def get_stats(self) -> CacheStats:
        with self._lock:
            l2_entries, l2_size = self.l2.get_stats()
            self._stats.l1_entries = self.l1.size()
            self._stats.l2_entries = l2_entries
            self._stats.l2_size_bytes = l2_size

            total = self._stats.hits + self._stats.misses
            self._stats.hit_rate = (self._stats.hits / total * 100.0) if total > 0 else 0.0
            self._stats.miss_rate = (self._stats.misses / total * 100.0) if total > 0 else 0.0

            return self._stats.model_copy()

    def _get_default_ttl(self, object_type: CacheObjectType) -> int:
        if object_type in (CacheObjectType.DOCUMENT_PARSE, CacheObjectType.DOCUMENT_CHUNK, CacheObjectType.EMBEDDING):
            return 86400 * 7  # 7 days
        if object_type in (CacheObjectType.SUMMARY, CacheObjectType.RESEARCH):
            return 3600 * 24  # 24 hours
        if object_type == CacheObjectType.RETRIEVAL:
            return 3600 * 2   # 2 hours
        return 300            # 5 minutes for Context and Discovery


# Global singleton instance
knowledge_cache = KnowledgeCache()
