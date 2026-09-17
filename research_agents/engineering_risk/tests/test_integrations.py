"""Tests for cross-agent and platform integrations (Agents #13, #14, #15, #16, #17, #18, #19, #20)."""
import pytest
from research_agents.engineering_risk.agent import EngineeringRiskAgent
from research_agents.engineering_risk.schemas import EngineeringRiskAgentInput

@pytest.mark.asyncio
async def test_integrations_lifecycle():
    agent = EngineeringRiskAgent()
    inp = EngineeringRiskAgentInput(
        project_id="proj_multi_agent_01",
        project={"title": "SAR Drone", "engineering_domain": "Robotics"},
        architecture={"subsystems": ["ThermalImaging", "PowerManagement"]},
        bom={"items": [{"component_id": "c1", "name": "FLIR"}]},
        requirements=[{"requirement_id": "REQ-001", "text": "Operate at 15 FPS"}],
        interfaces=[{"source": "COMP-JETSON-01", "target": "SUBSYS-COMPUTE"}],
        compliance_findings=[{"domain": "SAFETY", "status": "REVIEW"}],
        simulation_results=[{"domain": "THERMAL", "status": "FAIL"}],
    )
    out = await agent.run(inp)
    assert out.status == "success"
    assert out.dashboard is not None
    assert out.dashboard.total_risks >= 2
    assert "# Engineering Risk & FMEA Report" in out.structured_markdown_report
