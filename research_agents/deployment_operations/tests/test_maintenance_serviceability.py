"""Tests for maintenance and serviceability engine."""
from research_agents.deployment_operations.schemas import MaintenanceType, SystemType
from research_agents.deployment_operations.services.maintenance_serviceability_engine import MaintenanceServiceabilityEngine


def test_maintenance_tasks():
    engine = MaintenanceServiceabilityEngine()
    tasks = engine.create_maintenance_tasks("SYS-1", SystemType.HYBRID)
    assert len(tasks) >= 2
    # Check zero fabrication sentinel for condition-based task
    cond_task = next(t for t in tasks if t.maintenance_type == MaintenanceType.CONDITION_BASED)
    assert cond_task.interval == "MAINTENANCE_INTERVAL_UNKNOWN"


def test_serviceability_evaluations():
    engine = MaintenanceServiceabilityEngine()
    evals = engine.evaluate_serviceability("SYS-1", SystemType.PHYSICAL)
    assert len(evals) >= 2
    assert any(e.rating.value == "SERVICEABILITY_ACCEPTABLE" for e in evals)
