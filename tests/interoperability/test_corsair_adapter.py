"""Tests for Corsair Client, Registry, Tools, and Adapter."""

import pytest
from backend.workline.interoperability.corsair.adapter import CorsairAdapter
from backend.workline.interoperability.corsair.client import CorsairClient


@pytest.mark.asyncio
async def test_corsair_discovery_and_invocation():
    adapter = CorsairAdapter()
    integrations = await adapter.discover()
    assert len(integrations) >= 1
    assert any(i.agent_id == "ResearchAgent" for i in integrations)

    caps = await adapter.get_capabilities("ResearchAgent")
    assert any(c.capability_id == "research" for c in caps)

    # Invoke research tool
    res = await adapter.invoke(
        agent_id="ResearchAgent",
        capability="research",
        payload={"query": "LDO voltage regulator noise rejection"},
        task_id="TASK-CORSAIR-01",
    )

    assert res["status"] == "COMPLETED"
    assert "summary" in res
    assert "references" in res
    assert len(res["references"]) >= 1


@pytest.mark.asyncio
async def test_corsair_cancellation():
    adapter = CorsairAdapter()
    task_id = "TASK-CORSAIR-CANCEL"
    await adapter.client.invoke("ResearchAgent", "document_analysis", {}, task_id)
    cancelled = await adapter.cancel(task_id)
    assert cancelled is True
