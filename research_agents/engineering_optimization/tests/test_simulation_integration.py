"""
Test Agent #19 simulation integration: Agent #20 delegates to Agent #19, no duplicate engines.
"""
import pytest
from research_agents.engineering_optimization.schemas import (
    DesignCandidate, ObjectiveObject,
)
from research_agents.engineering_optimization.services.design_space_engine import DesignSpaceEngine


def test_simulation_results_override_proxy_objectives():
    """When simulation results are provided, they override proxy objective values."""
    engine = DesignSpaceEngine(random_seed=42)
    objectives = [
        ObjectiveObject(objective_id="OBJ-P", name="power_dissipation_watts",
                        direction="MINIMIZE", unit="W"),
    ]
    candidate = DesignCandidate(
        candidate_id="CAND-SIM",
        optimization_id="OPT-S",
        variable_values={"current_ma": 150.0, "voltage_v": 3.3},
    )
    # Simulate Agent #19 returning actual power value
    simulation_results = {"power_dissipation_watts": 0.495}
    candidate = engine.evaluate_objectives(candidate, objectives, simulation_results=simulation_results)
    assert candidate.objective_values["power_dissipation_watts"] == 0.495


def test_candidate_simulation_id_tracked():
    """Candidates linked to a simulation run should record the simulation_id."""
    c = DesignCandidate(
        candidate_id="CAND-LINKED",
        optimization_id="OPT-L",
        simulation_id="SIM-001",
    )
    assert c.simulation_id == "SIM-001"


def test_no_simulation_engine_in_design_space_engine():
    """DesignSpaceEngine must NOT contain a SimulationRunner — no duplicate engines."""
    engine = DesignSpaceEngine()
    # Verify no simulation runner attribute exists
    assert not hasattr(engine, "runner")
    assert not hasattr(engine, "simulation_runner")
    assert not hasattr(engine, "sim_runner")


def test_multiple_simulation_results_merged():
    """Multiple simulation result fields should all be mapped to objectives."""
    engine = DesignSpaceEngine()
    objectives = [
        ObjectiveObject(objective_id="OBJ-P", name="power_dissipation_watts", direction="MINIMIZE", unit="W"),
        ObjectiveObject(objective_id="OBJ-T", name="junction_temp_c", direction="MINIMIZE", unit="degC"),
    ]
    candidate = DesignCandidate(candidate_id="C1", optimization_id="OPT-M")
    sim_results = {"power_dissipation_watts": 0.495, "junction_temp_c": 47.27}
    candidate = engine.evaluate_objectives(candidate, objectives, simulation_results=sim_results)
    assert candidate.objective_values["power_dissipation_watts"] == 0.495
    assert candidate.objective_values["junction_temp_c"] == 47.27
