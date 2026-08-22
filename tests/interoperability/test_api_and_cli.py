"""Tests for Interoperability FastAPI endpoints and Typer CLI subcommands."""

import pytest
from fastapi.testclient import TestClient
from typer.testing import CliRunner

from backend.main import app
from cli.wline.main import app as cli_app

client = TestClient(app)
runner = CliRunner()


def test_api_agents_list_and_discover():
    # GET /api/agents
    res = client.get("/api/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) >= 2

    # POST /api/agents/discover
    res = client.post("/api/agents/discover", json={"protocol": "BINDU_A2A"})
    assert res.status_code == 200
    assert res.json()["total"] >= 2


def test_api_agent_details_and_capabilities():
    # GET /api/agents/{agent_id}
    res = client.get("/api/agents/ThermalSolver")
    assert res.status_code == 200
    data = res.json()
    assert data["agent"]["name"] == "ThermalSolver"
    assert "trust" in data

    # GET /api/agents/{agent_id}/capabilities
    res = client.get("/api/agents/ThermalSolver/capabilities")
    assert res.status_code == 200
    caps = res.json()
    assert len(caps) >= 2


def test_api_task_submission_and_lookup():
    # POST /api/agents/tasks
    res = client.post(
        "/api/agents/tasks",
        json={
            "project_id": "api_test_project",
            "team_id": "team_1",
            "target_agent": "ThermalSolver",
            "capability": "thermal_simulation",
            "payload": {"board_width": 50.0, "board_height": 50.0, "components": []},
            "human_approved": True,
        },
    )
    assert res.status_code == 200
    task = res.json()
    assert task["status"] == "COMPLETED"
    task_id = task["task_id"]

    # GET /api/agents/tasks/{task_id}
    res = client.get(f"/api/agents/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["task_id"] == task_id


def test_cli_agent_subcommands():
    # wline agent list
    res = runner.invoke(cli_app, ["agent", "list"])
    assert res.exit_code == 0
    assert "ThermalSolver" in res.stdout

    # wline agent discover
    res = runner.invoke(cli_app, ["agent", "discover"])
    assert res.exit_code == 0
    assert "EXTERNAL AGENTS" in res.stdout

    # wline agent info ThermalSolver
    res = runner.invoke(cli_app, ["agent", "info", "ThermalSolver"])
    assert res.exit_code == 0
    assert "AGENT DETAILS: ThermalSolver" in res.stdout

    # wline agent capabilities ThermalSolver
    res = runner.invoke(cli_app, ["agent", "capabilities", "ThermalSolver"])
    assert res.exit_code == 0
    assert "Thermal" in res.stdout and "Simulation" in res.stdout
