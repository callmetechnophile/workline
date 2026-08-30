"""
Unit tests for WaiverManager and active/expired waiver evaluation (Sections 43–46, 93, 94).
"""

from datetime import datetime, timedelta, timezone
from research_agents.engineering_compliance.schemas import ComplianceResult, ComplianceWaiver
from research_agents.engineering_compliance.services.gate_service import ComplianceGateService
from research_agents.engineering_compliance.services.waiver_manager import WaiverManager


def test_waiver_creation_and_expiration():
    mgr = WaiverManager()
    gate_service = ComplianceGateService()

    # Create active waiver
    w_active = mgr.create_waiver(
        project_id="p1",
        rule_id="RULE-ELEC-01",
        artifact_id="component:500-0771-01",
        reason="Lab supply variance",
        risk="Low",
        approved_by="safety_officer",
        duration_days=10,
    )
    assert mgr.is_waiver_expired(w_active) is False

    # Failure with active waiver -> ALLOW_WITH_APPROVED_EXCEPTION
    r_fail = ComplianceResult(
        compliance_id="C1",
        project_id="p1",
        artifact_id="component:500-0771-01",
        artifact_type="component",
        domain="ELECTRICAL",
        status="FAIL",
        severity="CRITICAL",
        rule_id="RULE-ELEC-01",
        description="Voltage violation",
    )
    s_waived = gate_service.evaluate_gate("p1", [r_fail], [w_active])
    assert s_waived.gate == "ALLOW_WITH_APPROVED_EXCEPTION"
    assert s_waived.status == "FAIL"  # Failure is NEVER disguised as PASS (Section 44)

    # Expired waiver -> BLOCK (Section 46 & 94)
    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    w_expired = ComplianceWaiver(
        waiver_id="W_EXP",
        project_id="p1",
        rule_id="RULE-ELEC-01",
        artifact_id="component:500-0771-01",
        reason="Expired",
        risk="Low",
        approved_by="officer",
        expires_at=past_date,
    )
    assert mgr.is_waiver_expired(w_expired) is True
    s_exp = gate_service.evaluate_gate("p1", [r_fail], [w_expired])
    assert s_exp.gate == "BLOCK"
