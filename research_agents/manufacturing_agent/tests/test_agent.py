"""Tests for ManufacturingDFMAgent Orchestrator."""
import pytest
from research_agents.manufacturing_agent.agent import ManufacturingDFMAgent
from research_agents.manufacturing_agent.schemas import ManufacturingAgentInput

@pytest.mark.asyncio
async def test_agent_run_full_analysis():
    agent = ManufacturingDFMAgent()
    inp = ManufacturingAgentInput(project_id="PROJ-FULL")
    out = await agent.run(inp)
    assert out.status == "success"
    assert len(out.processes) >= 1
    assert out.dashboard is not None

def test_agent_run_sync():
    agent = ManufacturingDFMAgent()
    inp = ManufacturingAgentInput(project_id="PROJ-SYNC")
    out = agent.run_sync(inp)
    assert out.status == "success"
    assert out.dashboard.total_components_analyzed >= 1
