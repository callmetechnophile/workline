"""Tests for basic cache operations, TTL expiration, and cleanup."""

import time
import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


def test_basic_cache_set_get_has_delete(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))

    key = "workline:test:basic_item"
    data = {"name": "Buck Regulator", "efficiency": 0.92}

    # Set
    cache.set(
        key=key,
        value=data,
        object_type=CacheObjectType.RETRIEVAL,
        options=CacheOptions(project_id="test_p1"),
    )

    # Has & Get
    assert cache.has(key, CacheObjectType.RETRIEVAL) is True
    retrieved = cache.get(key, CacheObjectType.RETRIEVAL)
    assert retrieved == data

    # Delete
    assert cache.delete(key, CacheObjectType.RETRIEVAL) is True
    assert cache.has(key, CacheObjectType.RETRIEVAL) is False
    assert cache.get(key, CacheObjectType.RETRIEVAL) is None


def test_cache_ttl_expiration_and_cleanup(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))

    key_short = "workline:test:short_ttl"
    key_long = "workline:test:long_ttl"

    # Set with 1 second TTL
    cache.set(
        key=key_short,
        value={"temp": 42},
        object_type=CacheObjectType.CONTEXT,
        options=CacheOptions(project_id="test_p1", ttl=1),
    )

    # Set with long TTL
    cache.set(
        key=key_long,
        value={"temp": 100},
        object_type=CacheObjectType.DOCUMENT_PARSE,
        options=CacheOptions(project_id="test_p1", ttl=60),
    )

    assert cache.get(key_short, CacheObjectType.CONTEXT) is not None
    assert cache.get(key_long, CacheObjectType.DOCUMENT_PARSE) is not None

    # Wait for short TTL to expire
    time.sleep(1.1)

    # Short TTL expired on access
    assert cache.get(key_short, CacheObjectType.CONTEXT) is None
    assert cache.get(key_long, CacheObjectType.DOCUMENT_PARSE) is not None

    # Clear expired
    cleared = cache.clear_expired()
    assert cleared >= 0
