"""
End-to-end integration and ADK capability tests for EngineeringSimulationAgent (Agent #19).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.engineering_simulation.agent import EngineeringSimulationAgent
from research_agents.engineering_simulation.providers.mock_provider import MockSimulationProvider
from research_agents.engineering_simulation.schemas import SimulationInput


@pytest.mark.asyncio
async def test_simulation_agent_full_run_and_export():
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = SimulationInput(
            project_id="proj_sar_drone_001",
            user_id="user_001",
            what_if_scenario="Test thermal margin under full load",
            output_dir=tmp_dir,
        )
        out = await agent.execute_simulation_cycle(inp)

        assert out.twin.project_id == "proj_sar_drone_001"
        assert len(out.exported_files) == 8

        dir_p = Path(tmp_dir)
        assert (dir_p / "digital_twin.json").exists()
        assert (dir_p / "model.json").exists()
        assert (dir_p / "simulation.json").exists()
        assert (dir_p / "simulation_result.json").exists()
        assert (dir_p / "scenario.json").exists()
        assert (dir_p / "sweep.json").exists()
        assert (dir_p / "simulation_evidence.json").exists()
        assert (dir_p / "simulation_report.md").exists()


def test_simulation_agent_sync_and_adk_capabilities():
    agent = EngineeringSimulationAgent(reasoning_provider=MockSimulationProvider())

    # ADK Methods
    res = agent.run_simulation("proj_sar_drone_001", voltage=3.3, current_ma=150.0)
    assert res.status == "PASS"
    assert res.outputs["power_dissipation_watts"] == 0.495

    scen = agent.run_scenario("proj_sar_drone_001", "Scenario 1", {"parameters": {"param": 10}})
    assert scen.scenario_id.startswith("SCEN-")

    swp = agent.run_parameter_sweep("SIM-01", "current_ma", 100.0, 200.0, 50.0)
    assert swp.samples == 3
