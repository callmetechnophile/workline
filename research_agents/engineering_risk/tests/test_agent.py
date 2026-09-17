"""End-to-end unit and integration tests for EngineeringRiskAgent."""
import pytest
from research_agents.engineering_risk.agent import EngineeringRiskAgent
from research_agents.engineering_risk.schemas import EngineeringRiskAgentInput

@pytest.mark.asyncio
async def test_agent_run_full_analysis():
    agent = EngineeringRiskAgent()
    inp = EngineeringRiskAgentInput(
        project_id="proj_sar_001",
        project={"title": "Search & Rescue Autonomous Drone", "engineering_domain": "Robotics"},
        architecture={"subsystems": ["ThermalImaging", "PowerManagement"]},
    )
    out = await agent.run(inp)
    assert out.status == "success"
    assert len(out.risks) >= 2
    assert len(out.failure_modes) >= 2
    assert len(out.fmea_records) >= 2
    assert len(out.mitigations) >= 2
    assert len(out.propagation_paths) >= 2
    assert out.dashboard is not None
    assert out.dashboard.total_risks >= 2

def test_agent_run_sync():
    agent = EngineeringRiskAgent()
    inp = EngineeringRiskAgentInput(
        project_id="proj_sync_001",
        project={"title": "High Altitude Platform", "engineering_domain": "Aerospace"},
    )
    out = agent.run_sync(inp)
    assert out.status == "success"
    assert out.dashboard.total_risks >= 2
