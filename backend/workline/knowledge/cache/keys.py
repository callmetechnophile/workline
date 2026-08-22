"""Deterministic cache-key generator for Python Knowledge Cache."""

import hashlib
from backend.workline.knowledge.cache.models import CacheObjectType


class CacheKeyGenerator:
    """Generates collision-resistant deterministic cache keys."""

    @classmethod
    def hash_str(cls, content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    @classmethod
    def generate_key(
        cls,
        object_type: CacheObjectType,
        project_id: str,
        identifier: str,
        config_hash: str = None,
        index_version: int = None,
    ) -> str:
        safe_id = cls.hash_str(identifier)[:24] if len(identifier) > 64 else identifier.replace(":", "_").replace(" ", "_")
        parts = ["workline", "knowledge", object_type.value.lower(), project_id, safe_id]

        if config_hash:
            parts.append(config_hash[:16])
        if index_version is not None:
            parts.append(f"v{index_version}")

        return ":".join(parts)

    @classmethod
    def generate_embedding_key(
        cls,
        content_hash: str,
        model: str,
        version: str = "v1",
        dimension: int = 384,
    ) -> str:
        return f"workline:knowledge:embedding:{content_hash[:24]}:{model}:{version}:{dimension}"

    @classmethod
    def generate_retrieval_key(
        cls,
        project_id: str,
        query: str,
        config_hash: str,
        index_version: int = 1,
    ) -> str:
        q_hash = cls.hash_str(query)[:24]
        return f"workline:knowledge:retrieval:{project_id}:{q_hash}:{config_hash[:12]}:idx{index_version}"

    @classmethod
    def generate_context_key(
        cls,
        project_id: str,
        query: str,
        knowledge_version: int,
    ) -> str:
        q_hash = cls.hash_str(query)[:24]
        return f"workline:knowledge:context:{project_id}:{q_hash}:kv{knowledge_version}"
