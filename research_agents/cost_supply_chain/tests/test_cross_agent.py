"""Cross-agent integration tests for Agent #25."""
from backend.armoriq.scope_map import AGENT_SCOPES
from research_agents.project_lifecycle_orchestrator.registry.agent_registry import AgentRegistry


def test_agent_registry_registration():
    registry = AgentRegistry()
    ag = registry.get_agent("Agent #25")
    assert ag is not None
    assert ag.agent_name == "CostSupplyChainAgent"
    assert "cost_estimation" in ag.capabilities
    assert "make_vs_buy_analysis" in ag.capabilities
    assert registry.is_agent_ready("CostSupplyChainAgent") is True


def test_armoriq_scope_map_registration():
    assert "CostSupplyChainAgent" in AGENT_SCOPES
    scopes = AGENT_SCOPES["CostSupplyChainAgent"]
    assert "cost.estimate" in scopes
    assert "cost.bom" in scopes
    assert "cost.make_buy" in scopes
    assert "cost.risk" in scopes
