"""Tests for multi-tenant isolation and security boundary enforcement."""
import pytest
from research_agents.deployment_operations.agent import DeploymentOpsAgent
from research_agents.deployment_operations.schemas import DeploymentOpsInput


@pytest.mark.asyncio
async def test_tenant_isolation_denied():
    agent = DeploymentOpsAgent()
    inp = DeploymentOpsInput(
        project_id="PROJ-SECRET",
        payload={"unauthorized_project_access": True},
    )
    out = await agent.run(inp)
    assert out.status == "access_denied"
    assert "PROJECT_ACCESS_DENIED" in (out.error_message or "")
