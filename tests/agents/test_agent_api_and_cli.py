"""Integration tests for Agent REST endpoints and API functionality."""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


def test_agent_api_endpoints():
    """Test POST /api/agents/run, GET /api/agents/executions/{id}, and POST /api/agents/approval/{id}."""
    client = TestClient(app)

    # 1. Run agent task
    res = client.post(
        "/api/agents/run",
        json={
            "project_id": "rover-api-test",
            "task": "Develop agricultural telemetry system",
            "user_id": "tester",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "execution_id" in data
    exec_id = data["execution_id"]
    assert data["status"] == "WAITING_FOR_USER"
    assert data["requires_user_action"] is True

    # 2. Get execution details
    res_status = client.get(f"/api/agents/executions/{exec_id}")
    assert res_status.status_code == 200
    details = res_status.json()
    assert details["execution_id"] == exec_id
    assert len(details["events"]) >= 4

    # 3. Submit checkpoint approval
    res_appr = client.post(
        f"/api/agents/approval/{exec_id}",
        json={"decision": "START_BUILD"},
    )
    assert res_appr.status_code == 200
    appr_data = res_appr.json()
    assert appr_data["status"] == "COMPLETED"

    # 4. Check project agent status
    res_proj = client.get("/api/agents/project/rover-api-test/status")
    assert res_proj.status_code == 200
    proj_status = res_proj.json()
    assert proj_status["status"] == "COMPLETED"
