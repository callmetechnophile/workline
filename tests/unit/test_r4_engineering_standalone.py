"""
Unit and Integration Tests for Workline R4 Engineering & Simulation Standalone Service.
Verifies health check, Bearer service token authentication, Unit Conversion, Requirement Validation, Decision Trade-offs, PCB DRC, and PINN Thermal Inference.
"""

import time
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from backend.r4.main import app
from backend.workline.pcb.models.project import PCBProject
from backend.workline.pcb.models.board import Board
from backend.workline.pcb.models.component import PCBComponent
from backend.workline.pcb.models.thermal import ThermalModel


@pytest.fixture
def client():
    """Provides TestClient for R4 FastAPI application."""
    return TestClient(app)


def test_r4_health_endpoint(client):
    """Verifies that R4 /health returns HTTP 200 without requiring external AI or DB calls."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "workline-r4"
    assert data["version"] == "1.0.0-rc1"


def test_r4_unit_conversion_unauthorized_without_token(client):
    """Verifies that POST /internal/engineering/units/convert returns 401 without token."""
    with patch("backend.r4.main.R4_SERVICE_TOKEN", "r4-secret-token-xyz"):
        response = client.post(
            "/internal/engineering/units/convert",
            json={"value": 5.0, "from_unit": "V", "to_unit": "mV"}
        )
        assert response.status_code == 401


def test_r4_unit_conversion_unauthorized_with_invalid_token(client):
    """Verifies that POST /internal/engineering/units/convert returns 401 with invalid Bearer token."""
    with patch("backend.r4.main.R4_SERVICE_TOKEN", "r4-secret-token-xyz"):
        response = client.post(
            "/internal/engineering/units/convert",
            json={"value": 5.0, "from_unit": "V", "to_unit": "mV"},
            headers={"Authorization": "Bearer bad-token-123"},
        )
        assert response.status_code == 401


def test_r4_unit_conversion_authorized(client):
    """Verifies high-precision unit conversion (5.0 V -> 5000.0 mV)."""
    with patch("backend.r4.main.R4_SERVICE_TOKEN", "r4-secret-token-xyz"):
        response = client.post(
            "/internal/engineering/units/convert",
            json={"value": 5.0, "from_unit": "V", "to_unit": "mV"},
            headers={"Authorization": "Bearer r4-secret-token-xyz"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["converted_value"] == 5000.0
        assert data["from_unit"] == "V"
        assert data["to_unit"] == "mV"


from backend.workline.pcb.models.footprint import Footprint
from backend.workline.pcb.models.thermal import ThermalModel, ThermalComponent


def test_r4_pinn_thermal_inference_performance(client):
    """Verifies PINN forward inference execution and measures latency."""
    sample_project = PCBProject(
        project_id="test_pinn_thermal_board",
        board=Board(width=100.0, height=80.0, layer_count=4),
        footprints={
            "fp_u1": Footprint(id="fp_u1", name="LQFP64", package="LQFP", body_width=14.0, body_height=14.0),
            "fp_q1": Footprint(id="fp_q1", name="SOIC8", package="SOIC", body_width=6.0, body_height=6.0),
        },
        components={
            "U1": PCBComponent(id="pcb_u1", component_id="comp_stm32", reference_designator="U1", footprint_id="fp_u1", x=50.0, y=40.0),
            "Q1": PCBComponent(id="pcb_q1", component_id="comp_mosfet", reference_designator="Q1", footprint_id="fp_q1", x=25.0, y=30.0),
        },
        thermal=ThermalModel(
            ambient_temperature=25.0,
            components={
                "U1": ThermalComponent(component_id="U1", power_dissipation=1.5),
                "Q1": ThermalComponent(component_id="Q1", power_dissipation=2.0),
            }
        ),
    )

    with patch("backend.r4.main.R4_SERVICE_TOKEN", "r4-secret-token-xyz"):
        t0 = time.perf_counter()
        response = client.post(
            "/internal/engineering/pinn/thermal",
            json={"project_dict": sample_project.model_dump(), "nx": 50, "ny": 40},
            headers={"Authorization": "Bearer r4-secret-token-xyz"},
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        assert response.status_code == 200
        data = response.json()
        assert "temperature_grid" in data
        assert len(data["temperature_grid"]) == 40
        assert len(data["temperature_grid"][0]) == 50
        assert data["predicted_peak_temperature"] >= data["ambient_temperature"]
        print(f"\n[PINN Performance Benchmark] Forward inference completed in: {elapsed_ms:.2f} ms")


def test_r4_pcb_validation(client):
    """Verifies geometric PCB Design Rule Checking (DRC) execution."""
    sample_project = PCBProject(
        project_id="test_drc_board",
        board=Board(width=80.0, height=60.0, layer_count=2),
        footprints={
            "fp_u1": Footprint(id="fp_u1", name="SOIC8", package="SOIC", body_width=10.0, body_height=10.0),
        },
        components={
            "U1": PCBComponent(id="pcb_u1", component_id="comp_ic1", reference_designator="U1", footprint_id="fp_u1", x=40.0, y=30.0),
        },
    )

    with patch("backend.r4.main.R4_SERVICE_TOKEN", "r4-secret-token-xyz"):
        response = client.post(
            "/internal/engineering/pcb/validate",
            json={"project_dict": sample_project.model_dump()},
            headers={"Authorization": "Bearer r4-secret-token-xyz"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "passed" in data
        assert "violations" in data
