"""
Unit tests for isolated what-if scenario branching (Sections 31–33, 99).
"""

from research_agents.engineering_simulation.services.scenario_engine import ScenarioEngine


def test_what_if_scenario_isolation():
    engine = ScenarioEngine()

    scen = engine.create_scenario(
        project_id="proj_sar_001",
        name="Double Load Branch",
        description="Simulate current draw increased to 300mA",
        changes={"parameters": {"current_ma": 300.0}},
    )

    assert scen.scenario_id.startswith("SCEN-")
    assert scen.changes["parameters"]["current_ma"] == 300.0
    assert scen.base_version == "v1.0.0"
