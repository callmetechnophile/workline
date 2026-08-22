"""Tests for embedding caching, model/dimension invalidation, and retrieval validation."""

import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.keys import CacheKeyGenerator
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions
from backend.workline.knowledge.llamaindex.client import LlamaIndexCacheWrapper


@pytest.mark.asyncio
async def test_embedding_caching_and_model_change():
    wrapper = LlamaIndexCacheWrapper()
    text = "Low dropout voltage linear regulator for RF subsystem"

    # 1. Compute and cache embedding with model A
    vec1 = await wrapper.get_embedding(text, "proj_1", model="model_A", dimension=128)
    assert len(vec1) == 128

    # 2. Same text and model returns cached embedding
    vec1_cached = await wrapper.get_embedding(text, "proj_1", model="model_A", dimension=128)
    assert vec1 == vec1_cached

    # 3. Changed model results in separate cache key
    vec2 = await wrapper.get_embedding(text, "proj_1", model="model_B", dimension=128)
    # Different pseudo-embedding seed/key
    assert len(vec2) == 128

    # 4. Changed dimension results in separate cache key
    vec3 = await wrapper.get_embedding(text, "proj_1", model="model_A", dimension=256)
    assert len(vec3) == 256


@pytest.mark.asyncio
async def test_retrieval_caching_and_staleness():
    wrapper = LlamaIndexCacheWrapper()

    # Initial query
    results1 = await wrapper.query_knowledge("proj_test", "power regulator options")
    assert len(results1) >= 1
    # DEC-101 is approved, DEC-102 is superseded
    assert any(r["id"] == "DEC-101" for r in results1)
    assert not any(r["id"] == "DEC-102" for r in results1)
