"""
Unit tests for ChangeApprovalEngine and No Self-Approval Rule (Sections 30–33, 77).
"""

import pytest
from research_agents.engineering_change_control.schemas import ChangeRequest
from research_agents.engineering_change_control.services.approval_engine import ChangeApprovalEngine


def test_approval_creation_and_self_approval_prevention():
    engine = ChangeApprovalEngine()

    chg = ChangeRequest(
        change_id="C_CRIT_01",
        project_id="p1",
        change_type="ARCHITECTURE_CHANGE",
        title="Critical Bus Redesign",
        description="Redesign SPI to UART",
        requested_by="engineer_alice",
        severity="CRITICAL",
    )

    approval = engine.create_approval_request(chg)
    assert approval is not None
    assert approval.status == "PENDING"
    assert approval.approval_type == "SAFETY_REVIEW"

    # 1. Self-approval blocked (Section 77)
    with pytest.raises(PermissionError, match="APPROVAL_DENIED"):
        engine.approve_change(approval, chg, approver_id="engineer_alice")

    # 2. Independent approver succeeds
    approved = engine.approve_change(approval, chg, approver_id="lead_bob")
    assert approved.status == "APPROVED"
    assert approved.approved_by == "lead_bob"
