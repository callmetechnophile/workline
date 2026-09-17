"""Integration tests for DeploymentOpsAgent."""
import pytest
from research_agents.deployment_operations.agent import DeploymentOpsAgent
from research_agents.deployment_operations.schemas import DeploymentOpsInput, ReadinessStatus, SystemType


@pytest.mark.asyncio
async def test_agent_full_run():
    agent = DeploymentOpsAgent()
    inp = DeploymentOpsInput(
        project_id="PROJ-AGENT-TEST",
        system_id="SYS-TEST-01",
        system_type=SystemType.HYBRID,
    )
    out = await agent.run(inp)
    assert out.status == "success"
    assert out.agent_id == "Agent #26"
    assert out.fabric_id == "agent.26"
    assert out.deployment_plan is not None
    assert out.commissioning_plan is not None
    assert out.operational_baseline is not None
    assert len(out.health_metrics) > 0
    assert len(out.maintenance_tasks) > 0
    assert len(out.spare_parts) > 0
    assert out.report_markdown is not None
