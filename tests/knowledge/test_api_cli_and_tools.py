"""Tests for Knowledge CLI commands, FastAPI endpoints, and Google ADK agent tools."""

from fastapi.testclient import TestClient
from typer.testing import CliRunner
import pytest

from backend.main import app
from backend.workline.agents.knowledge_tools import EngineeringKnowledgeTools
from backend.workline.knowledge import (
    Actor,
    ActorType,
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    EngineeringRequirement,
    RequirementCategory,
    knowledge_service,
)
from cli.wline.commands.decision import decision_app
from cli.wline.commands.finding import finding_app
from cli.wline.commands.knowledge import knowledge_app
from cli.wline.commands.lesson import lesson_app
from cli.wline.commands.requirement import requirement_app


def test_cli_knowledge_and_decision_commands():
    """Test 25: CLI commands for knowledge, decisions, requirements, findings, and lessons."""
    runner = CliRunner()

    # 1. wline decision create
    res_dec = runner.invoke(
        decision_app,
        ["create", "--title", "Select Motor Driver", "--selected", "DRV8871", "--rationale", "3.6A peak current", "--project", "proj_cli"],
    )
    assert res_dec.exit_code == 0
    assert "Decision created successfully" in res_dec.stdout

    # 2. wline requirement create
    res_req = runner.invoke(
        requirement_app,
        ["create", "--title", "Motor current capability", "--category", "ELECTRICAL", "--value", "3.0", "--unit", "A", "--project", "proj_cli"],
    )
    assert res_req.exit_code == 0
    assert "Requirement created" in res_req.stdout

    # 3. wline finding create
    res_find = runner.invoke(
        finding_app,
        ["create", "--title", "Motor driver overheating", "--description", "Observed 90C under stall test", "--category", "THERMAL", "--severity", "HIGH", "--project", "proj_cli"],
    )
    assert res_find.exit_code == 0, f"Error: {res_find.output}, {res_find.exception}"
    assert "Finding recorded" in res_find.stdout

    # 4. wline lesson create
    res_les = runner.invoke(
        lesson_app,
        ["create", "--title", "Motor stall thermal dissipation", "--context", "Chassis dyno test", "--cause", "Current limit set too high", "--impact", "Thermal shutdown", "--recommendation", "Add current sensing feedback loop", "--project", "proj_cli"],
    )
    assert res_les.exit_code == 0
    assert "Lesson learned recorded" in res_les.stdout

    # 5. wline knowledge search
    res_search = runner.invoke(
        knowledge_app,
        ["search", "motor driver thermal", "--project", "proj_cli"],
    )
    assert res_search.exit_code == 0
    assert "ENGINEERING KNOWLEDGE SEARCH RESULTS" in res_search.stdout


def test_fastapi_knowledge_endpoints():
    """Test 26: FastAPI REST API endpoints for knowledge layer."""
    client = TestClient(app)

    # 1. POST /api/knowledge/decisions
    res_create = client.post(
        "/api/knowledge/decisions",
        json={
            "decision_id": "DEC-API-01",
            "project_id": "proj_api",
            "title": "Select LoRa Module",
            "description": "Long range telemetry module",
            "category": "INTERFACE",
            "status": "PROPOSED",
            "created_by": {"actor_type": "HUMAN", "actor_id": "eng_lead"},
            "selected_option": "SX1262",
            "rationale": "Long range 15km, low power consumption",
        },
    )
    assert res_create.status_code == 200
    assert res_create.json()["decision_id"] == "DEC-API-01"

    # 2. POST /api/knowledge/decisions/{id}/approve
    res_app = client.post(
        "/api/knowledge/decisions/DEC-API-01/approve",
        json={"actor_id": "eng_lead", "actor_type": "HUMAN"},
    )
    assert res_app.status_code == 200
    assert res_app.json()["status"] == "APPROVED"

    # 3. GET /api/knowledge/decisions
    res_list = client.get("/api/knowledge/decisions?project_id=proj_api")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1

    # 4. POST /api/knowledge/search
    res_search = client.post(
        "/api/knowledge/search",
        json={"project_id": "proj_api", "query": "LoRa telemetry communication"},
    )
    assert res_search.status_code == 200
    assert len(res_search.json()) >= 1


def test_google_adk_knowledge_tools():
    """Test 27: Google ADK agent toolset interaction."""
    tools = EngineeringKnowledgeTools()

    # Create proposal via agent tool
    proposal = tools.create_decision_proposal(
        project_id="proj_adk",
        title="AI Proposed Battery Chemistry",
        category="POWER_ARCHITECTURE",
        problem="High energy density needed for 2h flight time",
        rationale="LiPo 4S 5000mAh offers 180Wh/kg",
        selected_option="LiPo 4S 5000mAh",
        agent_id="PowerAgent",
    )
    assert proposal["status"] == "PROPOSED"
    assert proposal["created_by"]["actor_type"] == "AGENT"

    # Agent cannot approve
    with pytest.raises(Exception):
        tools.approve_decision(proposal["decision_id"], actor_id="PowerAgent", actor_type="AGENT")

    # Human approves
    approved = tools.approve_decision(proposal["decision_id"], actor_id="lead_eng", actor_type="HUMAN")
    assert approved["status"] == "APPROVED"

    # Query current decisions
    current = tools.get_current_decisions("proj_adk")
    assert any(d["decision_id"] == proposal["decision_id"] for d in current)
