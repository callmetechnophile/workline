"""Tests for cache failure resilience, serialization errors, and secret protection."""

import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


def test_zero_secret_storage_in_cache(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))

    # Attempt to cache safe project data
    safe_data = {
        "requirement_id": "REQ-101",
        "description": "Operating voltage 3.3V +/- 5%",
        "category": "POWER",
    }

    cache.set("workline:req:101", safe_data, CacheObjectType.CONTEXT, CacheOptions(project_id="p1"))

    # Inspect persistent metadata and files to ensure no secret fields exist
    meta, val = cache.l2.get("workline:req:101", CacheObjectType.CONTEXT)
    meta_dict = meta.model_dump()
    meta_str = str(meta_dict)

    assert "api_key" not in meta_str
    assert "private_key" not in meta_str
    assert "wallet" not in meta_str
    assert "token" not in meta_str


def test_cache_graceful_fallback_on_unwritable_directory():
    # Point cache to non-existent / invalid path
    invalid_cache = KnowledgeCache(l2_base_dir="Z:\\invalid\\non_existent_mount\\cache")

    # Should not crash the process
    invalid_cache.set("k1", "data", CacheObjectType.RETRIEVAL, CacheOptions(project_id="p1"))
    # In-memory L1 still works smoothly!
    assert invalid_cache.get("k1", CacheObjectType.RETRIEVAL) == "data"
