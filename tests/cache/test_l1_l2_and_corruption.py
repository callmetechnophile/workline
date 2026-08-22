"""Tests for L1 memory cache, L2 persistent cache, and corrupted entry recovery."""

import os
import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


def test_l1_memory_hit_miss_and_eviction(tmp_path):
    # Cache with tiny L1 capacity: max 2 entries
    cache = KnowledgeCache(l1_max_entries=2, l2_base_dir=str(tmp_path / "cache"))

    cache.set("k1", "val1", CacheObjectType.RETRIEVAL, CacheOptions(project_id="p1"))
    cache.set("k2", "val2", CacheObjectType.RETRIEVAL, CacheOptions(project_id="p1"))

    # Hit
    assert cache.l1.get("k1") is not None
    assert cache.l1.get("k2") is not None

    # Miss
    assert cache.l1.get("k_nonexistent") is None

    # Insert 3rd item -> k1 (oldest accessed) evicted from L1 memory
    cache.l1.get("k2")  # refresh k2
    cache.set("k3", "val3", CacheObjectType.RETRIEVAL, CacheOptions(project_id="p1"))

    assert cache.l1.size() == 2
    # k1 was evicted from L1 memory, but still recoverable from L2 persistent disk!
    assert cache.l1.get("k1") is None
    recovered = cache.get("k1", CacheObjectType.RETRIEVAL)
    assert recovered == "val1"
    # Promoted back to L1
    assert cache.l1.get("k1") is not None


def test_l2_persistent_hit_miss_and_corruption_recovery(tmp_path):
    cache_dir = tmp_path / "cache"
    cache = KnowledgeCache(l2_base_dir=str(cache_dir))

    key = "workline:knowledge:doc:corrupt_test"
    cache.set(key, {"text": "Valid Doc"}, CacheObjectType.DOCUMENT_PARSE, CacheOptions(project_id="p1"))

    # Verify L2 hit
    assert cache.l2.get(key, CacheObjectType.DOCUMENT_PARSE) is not None

    # Manually corrupt the JSON file on disk
    path = cache.l2._get_path(key, CacheObjectType.DOCUMENT_PARSE)
    assert os.path.exists(path)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{invalid-corrupt-json-blob!!!")

    # Clear L1 to force L2 disk read
    cache.l1.clear()

    # Corrupt entry is safely discarded without crashing
    res = cache.get(key, CacheObjectType.DOCUMENT_PARSE)
    assert res is None
    # Corrupted file removed
    assert not os.path.exists(path)
