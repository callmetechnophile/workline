"""
Unit tests for ModelObject and DigitalTwin lifecycles (Sections 11 & 12).
"""

from research_agents.engineering_simulation.schemas import DigitalTwin, ModelAssumption, ModelObject


def test_model_and_digital_twin_creation():
    twin = DigitalTwin(
        twin_id="TWIN-001",
        project_id="p1",
        name="Drone Thermal Twin",
        version="v1.0.0",
    )
    assert twin.status == "DRAFT"
    assert twin.project_id == "p1"

    model = ModelObject(
        model_id="MOD-001",
        twin_id="TWIN-001",
        domain="POWER",
        description="Electro-thermal model",
        inputs=["voltage", "current_ma"],
        outputs=["power_dissipation_watts"],
        assumptions=[
            ModelAssumption(
                assumption_id="A1",
                model_id="MOD-001",
                description="Linear convective dissipation",
            )
        ],
    )
    assert model.domain == "POWER"
    assert len(model.assumptions) == 1
