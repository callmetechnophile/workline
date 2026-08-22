"""Tests for External Agent Registry and Trust Scoring."""

import pytest
from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    CapabilityType,
    RiskLevel,
)
from backend.workline.interoperability.registry import (
    AgentRegistry,
    AgentTrustRecord,
    ExternalAgent,
)


def test_agent_registration_and_retrieval():
    registry = AgentRegistry(cache_ttl_seconds=60.0)
    agent = ExternalAgent(
        agent_id="CustomSolver",
        name="Custom Solver Engine",
        description="Custom thermal and physics engine",
        provider="Acme Corp",
        protocol="BINDU_A2A",
        endpoint="bindu://acme/solver",
        capabilities=[
            AgentCapability(
                capability_id="thermal_simulation",
                agent_id="CustomSolver",
                name="Thermal Simulation",
                description="Simulates thermal effects",
                capability_type=CapabilityType.THERMAL_ANALYSIS,
                risk_level=RiskLevel.MEDIUM,
            )
        ],
    )

    registry.register_agent(agent)
    fetched = registry.get_agent("CustomSolver")
    assert fetched is not None
    assert fetched.name == "Custom Solver Engine"
    assert fetched.protocol == "BINDU_A2A"
    assert len(fetched.capabilities) == 1

    # Test listing and status update
    registry.update_status("CustomSolver", AgentStatus.BUSY)
    assert registry.get_agent("CustomSolver").status == AgentStatus.BUSY

    # Test unregister
    assert registry.unregister_agent("CustomSolver") is True
    assert registry.get_agent("CustomSolver") is None
    assert registry.unregister_agent("NonExistent") is False


def test_discovery_and_caching():
    registry = AgentRegistry(cache_ttl_seconds=10.0)
    
    # Discovery by protocol
    bindu_agents = registry.discover_agents(protocol="BINDU_A2A")
    assert len(bindu_agents) >= 2
    assert all(a.protocol == "BINDU_A2A" for a in bindu_agents)

    corsair_agents = registry.discover_agents(protocol="CORSAIR")
    assert len(corsair_agents) >= 1
    assert all(a.protocol == "CORSAIR" for a in corsair_agents)

    # Discovery by capability
    thermal_agents = registry.discover_agents(capability_type="thermal_simulation")
    assert len(thermal_agents) >= 1
    assert any(a.agent_id == "ThermalSolver" for a in thermal_agents)


def test_trust_scoring():
    record = AgentTrustRecord(agent_id="TestAgent")
    assert record.trust_score == 1.0

    record.successful_tasks = 10
    record.failed_tasks = 1
    record.timeouts = 1
    record.validation_failures = 0
    score = record.recompute_score()

    assert 0.0 < score <= 1.0
    assert score > 0.6  # Mostly successful

    # Heavy validation failures decrease trust
    record.validation_failures = 10
    lower_score = record.recompute_score()
    assert lower_score < score
