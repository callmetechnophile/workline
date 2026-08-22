"""Tests for targeted invalidation, knowledge versioning, and project/team isolation."""

import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.keys import CacheKeyGenerator
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


def test_targeted_source_and_project_invalidation(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))

    # Project A items
    k_a1 = "workline:knowledge:doc:a1"
    k_a2 = "workline:knowledge:chunk:a2"
    cache.set(k_a1, "content a1", CacheObjectType.DOCUMENT_PARSE, CacheOptions(project_id="proj_A", source_id="src_doc1"))
    cache.set(k_a2, "content a2", CacheObjectType.DOCUMENT_CHUNK, CacheOptions(project_id="proj_A", source_id="src_doc1"))

    # Project B item
    k_b1 = "workline:knowledge:doc:b1"
    cache.set(k_b1, "content b1", CacheObjectType.DOCUMENT_PARSE, CacheOptions(project_id="proj_B", source_id="src_doc2"))

    assert cache.has(k_a1, CacheObjectType.DOCUMENT_PARSE) is True
    assert cache.has(k_a2, CacheObjectType.DOCUMENT_CHUNK) is True
    assert cache.has(k_b1, CacheObjectType.DOCUMENT_PARSE) is True

    # Invalidate by source doc1 -> k_a1 and k_a2 deleted, k_b1 preserved
    count = cache.invalidate_by_source("src_doc1")
    assert count == 2
    assert cache.has(k_a1, CacheObjectType.DOCUMENT_PARSE) is False
    assert cache.has(k_a2, CacheObjectType.DOCUMENT_CHUNK) is False
    assert cache.has(k_b1, CacheObjectType.DOCUMENT_PARSE) is True

    # Invalidate by project B
    cache.invalidate_by_project("proj_B")
    assert cache.has(k_b1, CacheObjectType.DOCUMENT_PARSE) is False


def test_knowledge_version_context_invalidation():
    # Context key incorporates knowledge_version
    key_v1 = CacheKeyGenerator.generate_context_key("rover_proj", "regulator choices", knowledge_version=1)
    key_v2 = CacheKeyGenerator.generate_context_key("rover_proj", "regulator choices", knowledge_version=2)

    assert key_v1 != key_v2
    assert "kv1" in key_v1
    assert "kv2" in key_v2


def test_project_and_team_isolation(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))

    key_a = CacheKeyGenerator.generate_retrieval_key("proj_A", "thermal limits", "cfg1")
    key_b = CacheKeyGenerator.generate_retrieval_key("proj_B", "thermal limits", "cfg1")

    assert key_a != key_b
    assert "proj_A" in key_a
    assert "proj_B" in key_b

    cache.set(key_a, {"limit": 85.0}, CacheObjectType.RETRIEVAL, CacheOptions(project_id="proj_A", team_id="team_1"))

    # Project B cannot find key_b
    assert cache.get(key_b, CacheObjectType.RETRIEVAL) is None
    # Project A gets its data
    assert cache.get(key_a, CacheObjectType.RETRIEVAL)["limit"] == 85.0
