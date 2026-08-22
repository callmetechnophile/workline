"""Tests for Human Approval Workflow, Versioning, and Supersession."""

import pytest
from backend.workline.decision.models import DecisionStatus
from backend.workline.decision.service import DecisionService


def test_human_approval_lifecycle():
    """Test 19-22: Recommendation remains RECOMMENDED until approved by human."""
    service = DecisionService()
    dec = service.create_decision(
        decision_id="DEC-APP-01",
        project_id="rover_v2",
        title="Microcontroller Selection",
        description="Select primary MCU",
    )
    assert dec.status == DecisionStatus.DRAFT

    # Approve
    approved_dec = service.approve_decision("DEC-APP-01", approved_by="lead_engineer", role="OWNER")
    assert approved_dec.status == DecisionStatus.APPROVED
    assert "lead_engineer (OWNER)" in approved_dec.approved_by
    assert approved_dec.approved_at is not None


def test_decision_rejection():
    """Test rejection with rationale."""
    service = DecisionService()
    service.create_decision(
        decision_id="DEC-REJ-01",
        project_id="rover_v2",
        title="Battery Selection",
        description="Select LiPo pack",
    )

    rejected_dec = service.reject_decision("DEC-REJ-01", rejected_by="safety_officer", reason="Thermal margin too low")
    assert rejected_dec.status == DecisionStatus.REJECTED
    assert "Thermal margin too low" in rejected_dec.rationale


def test_decision_supersession():
    """Test 23-24: Superseding old decision preserves history and links new decision."""
    service = DecisionService()
    service.create_decision(
        decision_id="DEC-OLD-01",
        project_id="rover_v2",
        title="Old Motor Driver Selection",
        description="Original DRV8871 choice",
    )
    service.create_decision(
        decision_id="DEC-NEW-02",
        project_id="rover_v2",
        title="New Motor Driver Selection",
        description="Upgraded to TMC2209 for silent stepping",
    )

    superseded = service.supersede_decision("DEC-OLD-01", "DEC-NEW-02")
    assert superseded.status == DecisionStatus.SUPERSEDED
    assert superseded.superseded_by == "DEC-NEW-02"
