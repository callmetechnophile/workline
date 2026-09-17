"""Tests for SecurityThreatModelingAgent Orchestrator."""
import pytest
from research_agents.security_threat.agent import SecurityThreatModelingAgent
from research_agents.security_threat.schemas import SecurityThreatModelingAgentInput

@pytest.mark.asyncio
async def test_agent_run_full():
    agent = SecurityThreatModelingAgent()
    inp = SecurityThreatModelingAgentInput(project_id="PROJ-E2E")
    out = await agent.run(inp)
    assert out.status == "success"
    assert len(out.threats) >= 4
    assert out.dashboard is not None

def test_agent_run_sync():
    agent = SecurityThreatModelingAgent()
    inp = SecurityThreatModelingAgentInput(project_id="PROJ-SYNC")
    out = agent.run_sync(inp)
    assert out.status == "success"
    assert out.dashboard.total_threats >= 4
