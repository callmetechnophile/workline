"""Integration tests for CostSupplyChainAgent."""
import pytest
from research_agents.cost_supply_chain.agent import CostSupplyChainAgent
from research_agents.cost_supply_chain.schemas import CostSupplyChainInput


@pytest.mark.asyncio
async def test_agent_full_run():
    agent = CostSupplyChainAgent()
    inp = CostSupplyChainInput(project_id="PROJ-TEST-FULL")
    out = await agent.run(inp)
    assert out.status == "success"
    assert out.agent_id == "Agent #25"
    assert out.fabric_id == "agent.25"
    assert out.rollup is not None
    assert len(out.drivers) > 0
    assert len(out.risks) > 0
    assert out.dashboard is not None
    assert out.report_markdown is not None
