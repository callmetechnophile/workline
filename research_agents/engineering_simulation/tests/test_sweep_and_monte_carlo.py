"""
Unit tests for parameter sweeps and Monte Carlo uncertainty analysis (Sections 34–36, 78).
"""

from research_agents.engineering_simulation.services.simulation_runner import SimulationRunner


def test_parameter_sweep_and_monte_carlo():
    runner = SimulationRunner()

    # 1. Parameter Sweep
    sweep = runner.run_parameter_sweep("SIM-001", "current_ma", 100.0, 200.0, 25.0)
    assert sweep.samples == 5
    assert sweep.results[0]["current_ma"] == 100.0
    assert sweep.results[-1]["current_ma"] == 200.0

    # 2. Monte Carlo with Fixed Seed
    mc1 = runner.run_monte_carlo("SIM-001", samples=50, random_seed=42)
    mc2 = runner.run_monte_carlo("SIM-001", samples=50, random_seed=42)

    assert mc1["mean_junction_temp_c"] == mc2["mean_junction_temp_c"]
    assert mc1["random_seed"] == 42
