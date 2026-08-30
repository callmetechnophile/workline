"""
Unit tests for ComplianceGateService (Sections 40–42).
"""

from research_agents.engineering_compliance.schemas import ComplianceResult
from research_agents.engineering_compliance.services.gate_service import ComplianceGateService


def test_compliance_gate_allow_block_and_review():
    gate_service = ComplianceGateService()

    # 1. Clean PASS -> ALLOW
    r_pass = ComplianceResult(
        compliance_id="C1",
        project_id="p1",
        artifact_id="A1",
        artifact_type="component",
        domain="ELECTRICAL",
        status="PASS",
        severity="CRITICAL",
        rule_id="R1",
        description="Passed",
    )
    s_allow = gate_service.evaluate_gate("p1", [r_pass], [])
    assert s_allow.gate == "ALLOW"
    assert s_allow.blocking is False

    # 2. Critical FAIL -> BLOCK
    r_fail = ComplianceResult(
        compliance_id="C2",
        project_id="p1",
        artifact_id="A1",
        artifact_type="component",
        domain="ELECTRICAL",
        status="FAIL",
        severity="CRITICAL",
        rule_id="R1",
        description="Voltage violation",
    )
    s_block = gate_service.evaluate_gate("p1", [r_fail], [])
    assert s_block.gate == "BLOCK"
    assert s_block.blocking is True

    # 3. REVIEW -> REVIEW_REQUIRED
    r_rev = ComplianceResult(
        compliance_id="C3",
        project_id="p1",
        artifact_id="A1",
        artifact_type="component",
        domain="ELECTRICAL",
        status="REVIEW",
        severity="HIGH",
        rule_id="R1",
        description="Specification conflict",
    )
    s_rev = gate_service.evaluate_gate("p1", [r_rev], [])
    assert s_rev.gate == "REVIEW_REQUIRED"
