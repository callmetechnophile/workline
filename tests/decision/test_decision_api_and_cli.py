"""Tests for FastAPI endpoints and Typer CLI for Decision Engine."""

from fastapi.testclient import TestClient
import pytest
from typer.testing import CliRunner
from backend.main import app
from cli.wline.commands.decision import decision_app


@pytest.fixture
def client():
    return TestClient(app)


def test_fastapi_decision_endpoints(client):
    """Test REST API routes for decisions."""
    # 1. Create decision
    res = client.post(
        "/api/decisions",
        json={
            "decision_id": "DEC-API-01",
            "project_id": "rover_v2",
            "title": "Camera Sensor Choice",
            "description": "Select RGB camera sensor",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["decision_id"] == "DEC-API-01"

    # 2. Get decision
    res_get = client.get("/api/decisions/DEC-API-01")
    assert res_get.status_code == 200

    # 3. Approve decision
    res_app = client.post(
        "/api/decisions/DEC-API-01/approve",
        json={"approved_by": "vision_lead", "role": "ENGINEER"},
    )
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "APPROVED"


def test_cli_decision_commands():
    """Test CLI commands for decision engine."""
    runner = CliRunner()

    # wline decision create
    res_create = runner.invoke(
        decision_app,
        ["create", "--title", "LIDAR Sensor Selection", "--selected", "RPLIDAR A1", "--rationale", "360 deg 12m range", "--project", "rover_v2"],
    )
    assert res_create.exit_code == 0
    assert "Decision created successfully" in res_create.stdout

    # wline decision recommend
    res_rec = runner.invoke(
        decision_app,
        ["recommend", "REQ-101", "-p", "rover_v2"],
    )
    assert res_rec.exit_code == 0
    assert "WORKLINE ENGINEERING DECISION SUPPORT" in res_rec.stdout
    assert "TPS62130" in res_rec.stdout
    assert "ROBUST" in res_rec.stdout

    # wline decision compare
    res_comp = runner.invoke(
        decision_app,
        ["compare", "TPS62130", "LM2596-5"],
    )
    assert res_comp.exit_code == 0
    assert "TRADE-OFF MATRIX" in res_comp.stdout
