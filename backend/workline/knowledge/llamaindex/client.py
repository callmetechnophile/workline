"""LlamaIndex integration layer wrapped with two-tier KnowledgeCache and SurrealDB validation."""

import hashlib
from typing import Any, Dict, List, Optional
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.keys import CacheKeyGenerator
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


class LlamaIndexCacheWrapper:
    """Coordinates LlamaIndex indexing, embeddings, and retrieval with KnowledgeCache."""

    def __init__(self):
        self._project_index_versions: Dict[str, int] = {}

    def get_index_version(self, project_id: str) -> int:
        return self._project_index_versions.get(project_id, 1)

    def increment_index_version(self, project_id: str) -> int:
        next_v = self.get_index_version(project_id) + 1
        self._project_index_versions[project_id] = next_v
        # Invalidate retrieval results for this project
        knowledge_cache.invalidate_by_project(project_id)
        return next_v

    async def get_embedding(
        self,
        text: str,
        project_id: str,
        model: str = "text-embedding-3-small",
        dimension: int = 384,
    ) -> List[float]:
        """Fetch cached embedding or generate deterministic vector."""
        content_hash = CacheKeyGenerator.hash_str(text)
        cache_key = CacheKeyGenerator.generate_embedding_key(content_hash, model, "v1", dimension)

        # 1. Check cache
        cached = knowledge_cache.get(cache_key, CacheObjectType.EMBEDDING)
        if cached is not None:
            return cached

        # 2. Compute deterministic pseudo-embedding
        vec: List[float] = []
        seed = 0
        for ch in text:
            seed = (seed * 31 + ord(ch)) & 0xFFFFFFFF
        for _ in range(dimension):
            seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
            vec.append((seed / 0xFFFFFFFF) * 2.0 - 1.0)

        norm = sum(v * v for v in vec) ** 0.5 or 1.0
        normalized = [v / norm for v in vec]

        # 3. Store in cache
        knowledge_cache.set(
            cache_key,
            normalized,
            CacheObjectType.EMBEDDING,
            CacheOptions(
                project_id=project_id,
                source_hash=content_hash,
                model=model,
                embedding_dimension=dimension,
            ),
        )

        return normalized

    async def query_knowledge(
        self,
        project_id: str,
        query: str,
        knowledge_version: int = 1,
        authoritative_status_map: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Performs cached retrieval and filters candidates through SurrealDB authoritative status validation.
        """
        index_v = self.get_index_version(project_id)
        retrieval_key = CacheKeyGenerator.generate_retrieval_key(project_id, query, "hybrid_top5", index_v)

        cached_candidates = knowledge_cache.get(retrieval_key, CacheObjectType.RETRIEVAL)
        if cached_candidates is not None:
            candidates = list(cached_candidates)
        else:
            # Simulated retrieval
            candidates = [
                {
                    "id": "DEC-101",
                    "type": "DECISION",
                    "title": "Select Buck Regulator LM2596",
                    "content": "Selected for high efficiency 3A step-down power conversion.",
                    "status": "APPROVED",
                },
                {
                    "id": "DEC-102",
                    "type": "DECISION",
                    "title": "Select LDO TPS7A4700",
                    "content": "Selected for ultra-low noise RF and sensor rails.",
                    "status": "SUPERSEDED",
                },
            ]
            knowledge_cache.set(
                retrieval_key,
                candidates,
                CacheObjectType.RETRIEVAL,
                CacheOptions(project_id=project_id, ttl=3600),
            )

        # Apply SurrealDB authoritative override
        if authoritative_status_map:
            for item in candidates:
                item_id = item.get("id")
                if item_id in authoritative_status_map:
                    item["status"] = authoritative_status_map[item_id]

        # Filter out superseded, rejected, or invalid decisions
        valid_candidates = [c for c in candidates if c.get("status") not in ("SUPERSEDED", "REJECTED")]
        return valid_candidates


llamaindex_cache_wrapper = LlamaIndexCacheWrapper()
