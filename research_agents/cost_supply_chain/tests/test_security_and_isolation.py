"""Tests for multi-tenant isolation and security enforcement."""
import pytest
from research_agents.cost_supply_chain.agent import CostSupplyChainAgent
from research_agents.cost_supply_chain.schemas import CostSupplyChainInput


@pytest.mark.asyncio
async def test_tenant_boundary_denied():
    agent = CostSupplyChainAgent()
    inp = CostSupplyChainInput(
        project_id="PROJ-TENANT-X",
        payload={"unauthorized_project_access": True},
    )
    out = await agent.run(inp)
    assert out.status == "access_denied"
    assert "PROJECT_ACCESS_DENIED" in (out.error_message or "")
