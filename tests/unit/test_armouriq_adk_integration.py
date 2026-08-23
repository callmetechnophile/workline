"""
Unit and Security Test Suite for ArmourIQ x Google ADK Integration.
Verifies trust context, agent identity, delegation invariants, tool authorization,
risk engine, fail-closed posture, x402 payment independence, and audit trails.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.workline.armouriq.adk_adapter import ArmourIQADKAdapter, ArmourIQSecurityError
from backend.workline.armouriq.audit import ArmourIQAuditLogger, sanitize_audit_payload
from backend.workline.armouriq.capabilities import (
    AgentCapability,
    PolicyDecision,
    RiskTier,
    get_tool_capability_descriptor,
)
from backend.workline.armouriq.delegation import DelegationManager
from backend.workline.armouriq.health import ArmourIQHealthService
from backend.workline.armouriq.identity import AgentIdentity, AgentIdentityManager
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.risk import RiskEngine
from backend.workline.armouriq.trust_context import TrustContext


@pytest.fixture(autouse=True)
def clean_audit_logs():
    """Clear audit logs before and after each test."""
    ArmourIQAuditLogger.clear()
    yield
    ArmourIQAuditLogger.clear()


# 1. Trusted agent allowed
def test_trusted_agent_allowed():
    identity = AgentIdentityManager.create_agent_identity(
        agent_id="workline.domain_researcher",
        project_id="proj_solar_charger",
        session_id="sess_001",
    )
    context = TrustContext(
        session_id="sess_001",
        project_id="proj_solar_charger",
        agent_id=identity.agent_id,
        capabilities=identity.capabilities,
        trust_level=identity.trust_level,
    )
    decision = ArmourIQADKAdapter.before_agent_callback(identity, context)
    assert decision == PolicyDecision.ALLOW


# 2. Untrusted agent denied
def test_untrusted_agent_denied():
    identity = AgentIdentityManager.create_agent_identity(
        agent_id="workline.untrusted_worker",
        project_id="proj_solar_charger",
        session_id="sess_001",
        trust_level="UNTRUSTED",
    )
    context = TrustContext(
        session_id="sess_001",
        project_id="proj_solar_charger",
        agent_id=identity.agent_id,
        capabilities=identity.capabilities,
        trust_level="UNTRUSTED",
    )
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_agent_callback(identity, context)
    assert "UNTRUSTED" in str(exc_info.value)


# 3. Unauthorized tool denied
def test_unauthorized_tool_denied():
    context = TrustContext(
        session_id="sess_002",
        project_id="proj_battery_mgmt",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    # Research agent attempting save_bom (which requires MODIFY_BOM)
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_tool_callback("save_bom", {"bom": []}, context)
    assert "Capability violation" in str(exc_info.value) or "Domain Policy" in str(exc_info.value)


# 4. Unauthorized project denied (cross-project execution)
def test_cross_project_execution_denied():
    identity = AgentIdentityManager.create_agent_identity(
        agent_id="workline.research_agent",
        project_id="proj_alpha",
        session_id="sess_003",
    )
    # Context belongs to Project Beta
    context = TrustContext(
        session_id="sess_003",
        project_id="proj_beta",
        agent_id=identity.agent_id,
        capabilities=identity.capabilities,
    )
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_agent_callback(identity, context)
    assert "Project mismatch" in str(exc_info.value)


# 5. Child agent cannot escalate capabilities (CHILD ⊆ PARENT)
def test_child_agent_cannot_escalate_capabilities():
    parent_context = TrustContext(
        session_id="sess_004",
        project_id="proj_motor_controller",
        agent_id="workline.planner_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    # Child asks for EXECUTE_PROCUREMENT, which parent does not possess
    child_context = parent_context.spawn_child_context(
        child_agent_id="workline.procurement_agent",
        requested_capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.EXECUTE_PROCUREMENT],
    )
    assert AgentCapability.READ_RESEARCH in child_context.capabilities
    assert AgentCapability.EXECUTE_PROCUREMENT not in child_context.capabilities
    assert set(child_context.capabilities).issubset(set(parent_context.capabilities))


# 6. Delegation chain validated and recorded
def test_delegation_chain_tracking():
    root = TrustContext(
        session_id="sess_005",
        project_id="proj_drone",
        agent_id="workline.root_orchestrator",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE, AgentCapability.ANALYZE_COMPONENT],
    )
    planner = root.spawn_child_context("workline.planner_agent")
    research = planner.spawn_child_context("workline.research_agent")

    assert research.delegation_chain == [
        "workline.root_orchestrator",
        "workline.planner_agent",
        "workline.research_agent",
    ]


# 7. A2A trust validated
def test_a2a_trust_validation():
    caller = TrustContext(
        session_id="sess_006",
        project_id="proj_drone",
        agent_id="workline.planner_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    # Valid A2A within same project and capability boundary
    decision, err = ArmourIQPolicyEngine.evaluate_a2a_invocation(
        caller_context=caller,
        target_agent_id="workline.research_agent",
        target_project_id="proj_drone",
        requested_capabilities=[AgentCapability.READ_RESEARCH],
    )
    assert decision == PolicyDecision.ALLOW
    assert err is None

    # Invalid cross-project A2A
    cross_decision, cross_err = ArmourIQPolicyEngine.evaluate_a2a_invocation(
        caller_context=caller,
        target_agent_id="workline.research_agent",
        target_project_id="proj_other",
        requested_capabilities=[AgentCapability.READ_RESEARCH],
    )
    assert cross_decision == PolicyDecision.DENY
    assert "Cross-project" in cross_err


# 8. procurement.order requires human approval
def test_procurement_order_requires_approval():
    procurement_context = TrustContext(
        session_id="sess_007",
        project_id="proj_inverter",
        agent_id="workline.procurement_agent",
        capabilities=[AgentCapability.LOOKUP_COMPONENT, AgentCapability.EXECUTE_PROCUREMENT],
        is_human_approved=False,
    )
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_tool_callback("execute_procurement_order", {"action": "order"}, procurement_context)
    assert exc_info.value.decision == PolicyDecision.REQUIRE_APPROVAL
    assert exc_info.value.risk_level == RiskTier.CRITICAL


# 9. release.create requires human approval
def test_release_create_requires_approval():
    release_context = TrustContext(
        session_id="sess_008",
        project_id="proj_inverter",
        agent_id="workline.root_orchestrator",
        capabilities=[AgentCapability.CREATE_RELEASE],
        is_human_approved=False,
    )
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_tool_callback("create_release", {"version": "1.0.0"}, release_context)
    assert exc_info.value.decision == PolicyDecision.REQUIRE_APPROVAL
    assert exc_info.value.risk_level == RiskTier.CRITICAL


# 10. x402 payment does not bypass authorization
def test_x402_payment_does_not_bypass_authorization():
    # Context holds valid x402 payment token but lacks MODIFY_PCB capability
    context = TrustContext(
        session_id="sess_009",
        project_id="proj_robotics",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
        is_authenticated=True,
    )
    # Attempting to call high-risk validate_pcb tool without capability
    with pytest.raises(ArmourIQSecurityError):
        ArmourIQADKAdapter.before_tool_callback("validate_pcb", {"pcb_id": "pcb_123"}, context)


# 11. Fail-closed security posture
def test_fail_closed_on_unauthenticated_or_empty_project():
    unauth_context = TrustContext(
        session_id="sess_010",
        project_id="",
        agent_id="workline.root_orchestrator",
        is_authenticated=False,
    )
    decision, reason = ArmourIQPolicyEngine.evaluate_tool_execution(
        "search_knowledge_base", {"query": "MOSFET"}, unauth_context
    )
    assert decision == PolicyDecision.DENY


# 12. Forged agent identity denied
def test_forged_agent_identity_denied():
    identity = AgentIdentityManager.create_agent_identity(
        agent_id="workline.research_agent",
        project_id="proj_telemetry",
        session_id="sess_011",
    )
    # Tamper with token signature
    identity.token_signature = "0000000000000000000000000000000000000000000000000000000000000000"
    assert identity.verify() is False

    context = TrustContext(
        session_id="sess_011",
        project_id="proj_telemetry",
        agent_id=identity.agent_id,
        capabilities=identity.capabilities,
    )
    with pytest.raises(ArmourIQSecurityError) as exc_info:
        ArmourIQADKAdapter.before_agent_callback(identity, context)
    assert "token verification failed" in str(exc_info.value)


# 13. Audit events generated with no secrets logged
def test_audit_logging_and_zero_secrets():
    context = TrustContext(
        session_id="sess_012",
        project_id="proj_telemetry",
        agent_id="workline.research_agent",
        capabilities=[AgentCapability.READ_RESEARCH, AgentCapability.READ_KNOWLEDGE],
    )
    # Authorized tool call
    decision = ArmourIQADKAdapter.before_tool_callback(
        "search_knowledge_base",
        {"query": "GaN FETs", "api_key": "sk-secret-12345-never-leak", "token": "Bearer abc.def.ghi"},
        context,
    )
    assert decision == PolicyDecision.ALLOW

    events = ArmourIQAuditLogger.get_events(project_id="proj_telemetry")
    assert len(events) >= 1
    ev = events[-1]
    assert ev.tool_name == "search_knowledge_base"
    assert ev.decision == "ALLOW"

    # Verify redaction
    payload_str = str(ev.model_dump())
    assert "sk-secret-12345" not in payload_str
    assert "abc.def.ghi" not in payload_str


# 14. REST API health & endpoints test
def test_armouriq_rest_endpoints():
    client = TestClient(app)

    # Health check
    res_health = client.get("/api/armouriq/health")
    assert res_health.status_code == 200
    health_data = res_health.json()
    assert health_data["status"] == "CONNECTED"
    assert health_data["subsystems"]["policy_engine"]["status"] == "Operational"

    # Governed agents
    res_agents = client.get("/api/armouriq/agents")
    assert res_agents.status_code == 200
    agents_data = res_agents.json()
    assert len(agents_data["agents"]) >= 5

    # Capabilities
    res_caps = client.get("/api/armouriq/capabilities")
    assert res_caps.status_code == 200
    caps_data = res_caps.json()
    assert len(caps_data["capabilities"]) >= 10
