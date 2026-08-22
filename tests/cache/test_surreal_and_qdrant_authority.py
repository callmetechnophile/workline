"""Tests verifying SurrealDB authoritative overrides and Qdrant index version invalidation."""

import pytest
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.models import CacheObjectType
from backend.workline.knowledge.llamaindex.client import LlamaIndexCacheWrapper


@pytest.mark.asyncio
async def test_surrealdb_authoritative_status_overrides_cached_decision():
    wrapper = LlamaIndexCacheWrapper()

    # Query without live override: DEC-101 is returned (APPROVED)
    res_initial = await wrapper.query_knowledge("proj_rover", "regulators")
    assert any(d["id"] == "DEC-101" for d in res_initial)

    # Now simulate SurrealDB state change: DEC-101 has been marked SUPERSEDED in SurrealDB!
    authoritative_surreal_status = {"DEC-101": "SUPERSEDED"}

    # Query with live SurrealDB status map
    res_updated = await wrapper.query_knowledge(
        "proj_rover",
        "regulators",
        authoritative_status_map=authoritative_surreal_status,
    )

    # DEC-101 must NOT be returned as a valid decision even though it was cached!
    assert not any(d["id"] == "DEC-101" for d in res_updated)


def test_qdrant_index_version_change_invalidates_retrieval_cache(tmp_path):
    wrapper = LlamaIndexCacheWrapper()
    project_id = "proj_qdrant_v"

    v1 = wrapper.get_index_version(project_id)
    assert v1 == 1

    # Ingest / collection rebuild triggers index version increment
    v2 = wrapper.increment_index_version(project_id)
    assert v2 == 2

    # Verify old cache key differs from new index version key
    from backend.workline.knowledge.cache.keys import CacheKeyGenerator
    k_old = CacheKeyGenerator.generate_retrieval_key(project_id, "query", "cfg", index_version=v1)
    k_new = CacheKeyGenerator.generate_retrieval_key(project_id, "query", "cfg", index_version=v2)

    assert k_old != k_new
    assert "idx1" in k_old
    assert "idx2" in k_new
