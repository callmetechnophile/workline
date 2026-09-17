import pytest


def test_agent27_in_registry():
    from research_agents.project_lifecycle_orchestrator.registry.agent_registry import AgentRegistry
    registry = AgentRegistry()
    desc = registry.get_agent("TechDocAgent") or registry.get_agent("agent.27")
    assert desc is not None, "Agent #27 not registered in AgentRegistry"
    assert "create_document" in desc.capabilities


def test_armoriq_scope_map_for_agent27():
    from backend.armoriq.scope_map import AGENT_SCOPES
    assert "TechDocAgent" in AGENT_SCOPES
    scopes = AGENT_SCOPES["TechDocAgent"]
    assert "techdoc:create"           in scopes
    assert "techdoc:publish:controlled" in scopes
    assert "techdoc:approve"          in scopes
