"""
Unit tests for SimulationReportGenerator (Section 84).
"""

from research_agents.engineering_simulation.schemas import (
    DigitalTwin,
    ModelObject,
    ParameterSweepObject,
    ScenarioObject,
    SimulationObject,
    SimulationResult,
)
from research_agents.engineering_simulation.services.report_generator import SimulationReportGenerator


def test_simulation_23_section_report():
    generator = SimulationReportGenerator()

    twin = DigitalTwin(twin_id="TW1", project_id="p1", name="SAR Twin")
    model = ModelObject(model_id="M1", twin_id="TW1", domain="POWER", description="Desc")
    sim = SimulationObject(simulation_id="S1", project_id="p1", model_id="M1")
    res = SimulationResult(
        simulation_result_id="SR1",
        simulation_id="S1",
        status="PASS",
        outputs={"power_dissipation_watts": 0.495, "junction_temp_c": 47.28},
    )
    scen = ScenarioObject(scenario_id="SC1", project_id="p1", name="Scen 1", description="Desc")
    swp = ParameterSweepObject(
        sweep_id="SW1",
        simulation_id="S1",
        parameter_name="current_ma",
        range_min=100.0,
        range_max=200.0,
        step=50.0,
        samples=3,
    )

    report_md = generator.generate_report(
        twin=twin,
        models=[model],
        simulations=[sim],
        results=[res],
        scenarios=[scen],
        sweeps=[swp],
    )

    assert "# Engineering Simulation Report: p1" in report_md
    assert "## 23. Engineering Interpretation" in report_md
    assert "0.495" in report_md
