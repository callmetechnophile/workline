"""
Unit tests for SimulationRunner deterministic execution, timeouts, and hashing (Sections 22, 26, 79, 96, 98).
"""

from research_agents.engineering_simulation.schemas import ModelObject, SimulationObject
from research_agents.engineering_simulation.services.simulation_runner import SimulationRunner


def test_simulation_runner_execution_and_timeout():
    runner = SimulationRunner()

    model = ModelObject(
        model_id="M1",
        twin_id="TW1",
        domain="POWER",
        description="Electro-thermal model",
        parameters={"thermal_resistance": 45.0},
    )
    sim = SimulationObject(
        simulation_id="S1",
        project_id="p1",
        model_id="M1",
        inputs={"voltage": 3.3, "current_ma": 150.0},
        conditions={"ambient_temp_c": 25.0},
    )

    # 1. Deterministic PASS with SHA-256 hash (Section 96)
    res_pass = runner.run_simulation(sim, model)
    assert res_pass.status == "PASS"
    assert res_pass.outputs["power_dissipation_watts"] == 0.495
    assert res_pass.outputs["junction_temp_c"] == 47.27
    assert res_pass.hash is not None

    # 2. Timeout handling -> ERROR (Section 98)
    res_to = runner.run_simulation(sim, model, simulate_timeout=True)
    assert res_to.status == "ERROR"
    assert "SIMULATION_TIMEOUT" in res_to.metrics["error"]
