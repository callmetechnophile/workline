"""Tests for Cross-Agent & Platform Integrations."""
import pytest
from research_agents.security_threat.agent import SecurityThreatModelingAgent
from research_agents.security_threat.schemas import SecurityThreatModelingAgentInput

@pytest.mark.asyncio
async def test_full_platform_lifecycle_integration():
    agent = SecurityThreatModelingAgent()
    inp = SecurityThreatModelingAgentInput(
        project_id="PROJ-INTEGRATION-01",
        project={"title": "Multi-Agent SAR Platform"},
        architecture={"subsystems": ["ThermalImaging", "PowerManagement"]},
        api_definitions=[{"endpoint": "/api/v1/sensors", "method": "POST"}],
        change_request={"change_id": "CHG-001", "project_id": "PROJ-INTEGRATION-01", "target_artifact": "API"},
    )
    out = await agent.run(inp)
    assert out.status == "success"
    assert len(out.assets) >= 4
    assert len(out.threats) >= 4
    assert len(out.security_controls) >= 4
    assert len(out.security_tests) >= 4
    assert out.change_impact is not None
    assert "# Security & Threat Modeling Report" in out.structured_markdown_report
