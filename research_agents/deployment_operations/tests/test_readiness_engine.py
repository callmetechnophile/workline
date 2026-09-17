"""Tests for readiness engine."""
from research_agents.deployment_operations.schemas import ReadinessStatus, SystemType
from research_agents.deployment_operations.services.readiness_engine import ReadinessEngine


def test_readiness_pass():
    engine = ReadinessEngine()
    status, criteria = engine.evaluate_readiness(
        project_id="PROJ-OK",
        system_type=SystemType.HYBRID,
        components=[],
        known_risks=[],
        dfm_handoff={"readiness_score": 0.95},
        supply_chain_handoff={"unpriced_parts_count": 0},
    )
    assert status == ReadinessStatus.READY
    assert all(not c.is_blocking for c in criteria)


def test_readiness_blocked_by_dfm():
    engine = ReadinessEngine()
    status, criteria = engine.evaluate_readiness(
        project_id="PROJ-DFM-FAIL",
        system_type=SystemType.PHYSICAL,
        components=[],
        known_risks=[],
        dfm_handoff={"readiness_score": 0.50},
    )
    assert status == ReadinessStatus.BLOCKED
    assert any(c.is_blocking and "DFM" in c.name for c in criteria)


def test_readiness_blocked_by_safety():
    engine = ReadinessEngine()
    status, criteria = engine.evaluate_readiness(
        project_id="PROJ-SAFE-FAIL",
        system_type=SystemType.PHYSICAL,
        components=[],
        known_risks=[{"severity": "CRITICAL", "description": "High voltage arc flash risk"}],
    )
    assert status == ReadinessStatus.BLOCKED
    assert any(c.is_blocking and "Safety" in c.name for c in criteria)
