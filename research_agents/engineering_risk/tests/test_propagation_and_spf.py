"""Tests for Fault Propagation, SPF, Cascading, and Common-Cause (Sections 98, 99)."""
from research_agents.engineering_risk.schemas import FailureMode
from research_agents.engineering_risk.services.propagation_engine import PropagationEngine

def test_single_point_failure():
    # Section 98: Component A -> critical subsystem -> system (No redundant path) -> SINGLE_POINT_FAILURE
    engine = PropagationEngine()
    fm = FailureMode(
        failure_mode_id="FM-SPF-01",
        component_id="COMP-MAIN-MCU",
        subsystem_id="SUBSYS-CONTROLLER",
        description="Main microcontroller crash",
        is_single_point_failure=True,
        redundancy_present=False,
    )
    prop = engine.analyze_propagation(fm)
    assert prop.is_single_point_failure is True
    assert "COMP-MAIN-MCU" in prop.path

def test_cascading_failure_path():
    # Section 99: Component A fails -> Power fails -> Controller fails -> System lost
    engine = PropagationEngine()
    fm = FailureMode(
        failure_mode_id="FM-CASCADE-01",
        component_id="COMP-PMIC",
        subsystem_id="SUBSYS-POWER",
        description="PMIC short circuit",
    )
    interfaces = [
        {"source": "COMP-PMIC", "target": "SUBSYS-POWER"},
        {"source": "SUBSYS-POWER", "target": "SUBSYS-CONTROLLER"},
        {"source": "SUBSYS-CONTROLLER", "target": "SUBSYS-PAYLOAD"},
    ]
    prop = engine.analyze_propagation(fm, interfaces=interfaces)
    assert len(prop.path) >= 3
    assert prop.is_cascading is True
    assert prop.path == ["COMP-PMIC", "SUBSYS-POWER", "SUBSYS-CONTROLLER", "SUBSYS-PAYLOAD"]
