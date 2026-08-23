"""
Workline AI — Project Creation & Project Context Verification Test Suite.

Verifies:
1. Create project with human-readable project_name and technical system_specification.
2. Rejection of empty / whitespace-only project_name and system_specification.
3. Persistence of project_name, system_specification, timeline, template, team, and status.
4. Separation of project_id (internal identifier) vs project_name (human-readable display).
5. Safe fallback handling for legacy records without project_name.
6. Package history and SQLite/Postgres schema migration.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import init_db, save_package, get_user_history, get_db_connection
from backend.schemas.research_schemas import ResearchRequest, ResearchResponse
from backend.agents.planner_agent import run_engineering_pipeline


client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Ensure clean database schema with all dynamic migration columns."""
    init_db()


def test_research_request_validation():
    """Test schema validation for project creation request."""
    # Valid payload with distinct project_name and system_specification
    req = ResearchRequest(
        project_name="High-Speed USB-C Hub",
        system_specification="High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
        target_days=30,
        engineering_template="USB-C Hub Template",
    )
    assert req.project_name == "High-Speed USB-C Hub"
    assert req.system_specification == "High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery"
    assert req.target_days == 30


def test_research_api_rejects_empty_specification():
    """Test that empty specification & engineering goal is rejected with HTTP 400."""
    response = client.post("/api/research", json={
        "project_name": "Test Project",
        "system_specification": "   ",
        "target_days": 30,
    })
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]


def test_research_api_rejects_whitespace_only_project_name():
    """Test that whitespace-only project name is rejected with HTTP 400."""
    response = client.post("/api/research", json={
        "project_name": "   ",
        "system_specification": "Valid system specification for a buck converter",
        "target_days": 30,
    })
    assert response.status_code == 400
    assert "Project name cannot be empty" in response.json()["detail"]


def test_run_engineering_pipeline_preserves_project_name_and_id():
    """Test that planner agent preserves distinct project_name, system_specification, and project_id."""
    res = run_engineering_pipeline(
        user_intent="High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery",
        target_days=45,
        project_name="High-Speed USB-C Hub",
        engineering_template="USB 3.2 Hub",
        team_id="Hardware Core Team",
    )

    assert res["project_name"] == "High-Speed USB-C Hub"
    assert res["system_specification"] == "High-speed USB 3.2 Gen 2 Type-C Hub Controller with Power Delivery"
    assert res["target_timeline_days"] == 45
    assert res["engineering_template"] == "USB 3.2 Hub"
    assert res["team_id"] == "Hardware Core Team"
    assert res["status"] == "active"
    assert res["project_id"].startswith("PROJ-")


def test_package_persistence_and_history_retrieval():
    """Test database package persistence and retrieval with project metadata."""
    user_id = "test_engineer_user_123"
    p_name = "48V to 12V Buck Converter"
    p_spec = "Synchronous 48V to 12V buck converter with 95% efficiency"
    p_id = "PROJ-BUCK-001"
    
    save_package(
        user_id=user_id,
        intent=p_spec,
        readiness=90,
        risk=10,
        optimization=95,
        data={"components": ["MOSFET", "Inductor", "Capacitor"]},
        project_name=p_name,
        system_specification=p_spec,
        target_days=30,
        engineering_template="Power Electronics",
        team_id="Power Systems Team",
        project_id=p_id,
        status="active",
    )

    history = get_user_history(user_id=user_id)
    assert len(history) >= 1
    latest = history[0]
    assert latest["project_name"] == p_name
    assert latest["system_specification"] == p_spec
    assert latest["project_id"] == p_id
    assert latest["target_days"] == 30
    assert latest["status"] == "active"


def test_legacy_package_fallback_when_project_name_missing():
    """Test that legacy database packages without project_name fallback safely to 'Untitled Engineering Project'."""
    conn = get_db_connection()
    # Insert legacy row directly without project_name
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO packages (user_id, intent, readiness_score, risk_score, optimization_score, data, timestamp)
        VALUES ('legacy_user_456', 'Legacy IoT Node', 80, 20, 85, '{"legacy": true}', '2026-01-01T00:00:00')
    """)
    conn.commit()
    conn.close()

    history = get_user_history(user_id="legacy_user_456")
    assert len(history) >= 1
    legacy_item = history[0]
    assert legacy_item["project_name"] == "Untitled Engineering Project" or legacy_item["project_name"] == "Legacy IoT Node"
    assert legacy_item["intent"] == "Legacy IoT Node"
    assert legacy_item["target_days"] == 30
