"""Tests for commissioning engine."""
from research_agents.deployment_operations.schemas import CommissioningStatus, SystemType
from research_agents.deployment_operations.services.commissioning_engine import CommissioningEngine


def test_commissioning_plan():
    engine = CommissioningEngine()
    plan = engine.create_commissioning_plan(
        project_id="PROJ-1",
        system_id="SYS-1",
        system_type=SystemType.HYBRID,
    )
    assert len(plan.tests) >= 5
    assert plan.overall_status == CommissioningStatus.NOT_RUN
    subsystems = [t.subsystem for t in plan.tests]
    assert "CORE_POWER" in subsystems
    assert "SAFETY_CONTROL" in subsystems
