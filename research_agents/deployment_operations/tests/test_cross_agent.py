"""Cross-agent integration tests for Agent #26."""
from backend.armoriq.scope_map import AGENT_SCOPES
from research_agents.project_lifecycle_orchestrator.registry.agent_registry import AgentRegistry


def test_agent_registry_presence():
    registry = AgentRegistry()
    ag = registry.get_agent("Agent #26")
    assert ag is not None
    assert ag.agent_name == "DeploymentOpsAgent"
    assert "deployment_analysis" in ag.capabilities
    assert "commissioning_planning" in ag.capabilities
    assert "spare_parts_planning" in ag.capabilities
    assert registry.is_agent_ready("DeploymentOpsAgent") is True


def test_armoriq_scope_map_presence():
    assert "DeploymentOpsAgent" in AGENT_SCOPES
    scopes = AGENT_SCOPES["DeploymentOpsAgent"]
    assert "ops.deployment" in scopes
    assert "ops.readiness" in scopes
    assert "ops.commissioning" in scopes
    assert "ops.maintenance" in scopes
