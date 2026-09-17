"""Tests for operational modes and decommissioning."""
from research_agents.deployment_operations.schemas import OperationalMode
from research_agents.deployment_operations.services.decommission_engine import DecommissionEngine
from research_agents.deployment_operations.services.operational_mode_engine import OperationalModeEngine


def test_mode_matrix():
    engine = OperationalModeEngine()
    matrix = engine.get_mode_matrix()
    assert OperationalMode.NORMAL.value in matrix
    assert OperationalMode.DEGRADED.value in matrix
    assert len(matrix[OperationalMode.DEGRADED.value]["permitted"]) > 0


def test_decommission_plan():
    engine = DecommissionEngine()
    plan = engine.create_decommissioning_plan("PROJ-1", "SYS-1")
    assert len(plan.shutdown_sequence) >= 3
    assert len(plan.data_preservation_steps) >= 3
