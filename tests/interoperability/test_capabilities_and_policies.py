"""Tests for Capability Risk Levels, Schemas, and Policy Enforcement."""

import pytest
from backend.workline.interoperability.capabilities import (
    AgentCapability,
    AgentStatus,
    CapabilityType,
    RiskLevel,
)
from backend.workline.interoperability.policies import PolicyEngine
from backend.workline.interoperability.registry import ExternalAgent
from backend.workline.interoperability.validation import AgentResultValidator


def test_policy_authorization_rules():
    agent = ExternalAgent(
        agent_id="SafeAgent",
        name="Safe Agent",
        description="Safe low-risk research agent",
        status=AgentStatus.AVAILABLE,
        capabilities=[
            AgentCapability(
                capability_id="research",
                agent_id="SafeAgent",
                name="Research",
                description="Low risk research",
                risk_level=RiskLevel.LOW,
            ),
            AgentCapability(
                capability_id="production_deploy",
                agent_id="SafeAgent",
                name="Production Deploy",
                description="Critical deployment",
                risk_level=RiskLevel.CRITICAL,
            ),
        ],
    )

    # 1. Valid Low-Risk Task
    is_auth, err = PolicyEngine.evaluate_task_authorization(
        project_id="test_p1",
        team_id="team_alpha",
        requesting_agent="User",
        target_agent=agent,
        capability=agent.capabilities[0],
    )
    assert is_auth is True
    assert err is None

    # 2. Critical Risk Task without Human Approval -> Rejected
    is_auth, err = PolicyEngine.evaluate_task_authorization(
        project_id="test_p1",
        team_id="team_alpha",
        requesting_agent="User",
        target_agent=agent,
        capability=agent.capabilities[1],
        human_approved=False,
    )
    assert is_auth is False
    assert "CRITICAL risk" in err

    # 3. Critical Risk Task with Human Approval -> Authorized
    is_auth, err = PolicyEngine.evaluate_task_authorization(
        project_id="test_p1",
        team_id="team_alpha",
        requesting_agent="User",
        target_agent=agent,
        capability=agent.capabilities[1],
        human_approved=True,
    )
    assert is_auth is True

    # 4. Target Agent Offline -> Rejected
    agent.status = AgentStatus.OFFLINE
    is_auth, err = PolicyEngine.evaluate_task_authorization(
        project_id="test_p1",
        team_id="team_alpha",
        requesting_agent="User",
        target_agent=agent,
        capability=agent.capabilities[0],
    )
    assert is_auth is False
    assert "not available" in err


def test_result_schema_validation():
    cap = AgentCapability(
        capability_id="thermal_simulation",
        agent_id="ThermalSolver",
        name="Thermal Simulation",
        description="Simulates temperature",
        output_schema={
            "type": "object",
            "required": ["max_temperature", "status"],
            "properties": {
                "max_temperature": {"type": "number"},
                "status": {"type": "string"},
            },
        },
    )

    # Valid result
    valid_res = {"max_temperature": 55.4, "status": "COMPLETED", "hotspots": []}
    is_valid, errors = AgentResultValidator.validate_result(cap, valid_res)
    assert is_valid is True
    assert len(errors) == 0

    # Invalid result: missing required field
    invalid_res1 = {"status": "COMPLETED"}
    is_valid, errors = AgentResultValidator.validate_result(cap, invalid_res1)
    assert is_valid is False
    assert any("max_temperature" in e for e in errors)

    # Invalid result: wrong data type
    invalid_res2 = {"max_temperature": "HOT", "status": "COMPLETED"}
    is_valid, errors = AgentResultValidator.validate_result(cap, invalid_res2)
    assert is_valid is False
    assert any("expected number" in e for e in errors)
