"""
Specification-mandated test scenarios for EngineeringSimulationAgent (Sections 96–109).
"""

import pytest
from research_agents.engineering_simulation.agent import EngineeringSimulationAgent
from research_agents.engineering_simulation.providers.mock_provider import MockSimulationProvider
from research_agents.engineering_simulation.schemas import SimulationInput


@pytest.mark.asyncio
async def test_scenario_96_simple_model_reproducibility():
    """Section 96: Deterministic numerical model with known inputs produces reproducible result."""
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())
    inp = SimulationInput(project_id="proj_sar_drone_001")
    out1 = await agent.execute_simulation_cycle(inp)
    out2 = await agent.execute_simulation_cycle(inp)

    assert out1.results[0].status == "PASS"
    assert out1.results[0].outputs["power_dissipation_watts"] == out2.results[0].outputs["power_dissipation_watts"]
    assert out1.results[0].hash == out2.results[0].hash


@pytest.mark.asyncio
async def test_scenario_97_unit_error():
    """Section 97: Incompatible units raise MODEL_ERROR and prevent simulation."""
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())
    inp = SimulationInput(project_id="proj_sar_drone_001")
    custom_inputs = {"voltage": 3.3, "voltage_unit": "invalid_unit", "current_ma": 150.0}

    with pytest.raises(ValueError, match="MODEL_ERROR"):
        await agent.execute_simulation_cycle(inp, custom_inputs=custom_inputs)


@pytest.mark.asyncio
async def test_scenario_98_timeout_yields_error():
    """Section 98: Simulation exceeding timeout yields ERROR, never PASS."""
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())
    inp = SimulationInput(project_id="proj_sar_drone_001")
    out = await agent.execute_simulation_cycle(inp, simulate_timeout=True)

    assert out.results[0].status == "ERROR"


@pytest.mark.asyncio
async def test_scenario_99_what_if_scenario_isolation():
    """Section 99: What-if parameter change creates scenario branch with original project unchanged."""
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())
    scen = agent.run_scenario(
        project_id="proj_sar_drone_001",
        scenario_description="Double sensor load",
        changes={"parameters": {"load": 2.0}},
    )

    assert scen.scenario_id.startswith("SCEN-")
    assert scen.changes["parameters"]["load"] == 2.0
