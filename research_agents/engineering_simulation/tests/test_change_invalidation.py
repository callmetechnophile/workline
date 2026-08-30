"""
Unit tests for change-driven simulation invalidation and stale model detection (Sections 60–62, 100).
"""

from research_agents.engineering_simulation.schemas import ModelObject, SimulationObject
from research_agents.engineering_simulation.services.resimulation_engine import ReSimulationEngine


def test_change_invalidation_and_stale_models():
    engine = ReSimulationEngine()

    m1 = ModelObject(
        model_id="M1",
        twin_id="TW1",
        domain="POWER",
        description="Lepton 3.5 Sensor Core Model",
        parameters={"thermal_resistance": 45.0},
    )
    s1 = SimulationObject(
        simulation_id="SIM-001",
        project_id="p1",
        model_id="M1",
        inputs={"voltage": 3.3},
    )

    stale_models, inv_sims, req_resim = engine.process_change_impact(
        target_artifact="Lepton",
        models=[m1],
        simulations=[s1],
    )

    assert "M1" in stale_models
    assert "SIM-001" in inv_sims
    assert "SIM-001" in req_resim
