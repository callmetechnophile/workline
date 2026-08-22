"""Tests for Decision Models and Candidate Eligibility Filtering."""

import pytest
from backend.workline.decision.models import (
    CriterionCategory,
    CriterionDirection,
    DecisionCandidate,
    DecisionCriterion,
    DecisionStatus,
    DecisionType,
    EngineeringDecision,
)
from backend.workline.decision.service import DecisionService


def test_decision_model_creation():
    """Test 1: Decision model initialization and default properties."""
    decision = EngineeringDecision(
        decision_id="DEC-TEST-001",
        project_id="rover_v2",
        title="Select 3.3V Step-Down Regulator",
        description="Select regulator capable of 3.3V @ 2A from 5V bus.",
        status=DecisionStatus.DRAFT,
        decision_type=DecisionType.COMPONENT_SELECTION,
    )
    assert decision.decision_id == "DEC-TEST-001"
    assert decision.status == DecisionStatus.DRAFT
    assert decision.version == 1
    assert decision.stability == "ROBUST"


def test_candidate_eligibility_filtering():
    """Test 2-4: Candidate eligibility (PASS, FAIL, UNKNOWN, CONFLICTED)."""
    service = DecisionService()
    dec = service.create_decision(
        decision_id="DEC-ELIG-01",
        project_id="rover_v2",
        title="Regulator Selection",
        description="Testing eligibility filter",
    )

    cand_pass = DecisionCandidate(
        candidate_id="cand_1",
        entity_id="comp_tps",
        name="TPS62130",
        eligibility_status="ELIGIBLE",
    )
    cand_fail = DecisionCandidate(
        candidate_id="cand_2",
        entity_id="comp_bad",
        name="BadReg",
        eligibility_status="INELIGIBLE",
    )
    cand_unknown = DecisionCandidate(
        candidate_id="cand_3",
        entity_id="comp_unk",
        name="UnknownReg",
        eligibility_status="UNKNOWN",
    )
    cand_conflicted = DecisionCandidate(
        candidate_id="cand_4",
        entity_id="comp_conf",
        name="ConflictReg",
        eligibility_status="CONFLICTED",
    )

    raw_matrix = {
        "cand_1": {"crit_tech": 0.95, "crit_cost": 0.80, "crit_avail": 0.90, "crit_risk": 0.90},
        "cand_2": {"crit_tech": 0.10, "crit_cost": 0.99, "crit_avail": 0.90, "crit_risk": 0.90},
    }

    # Generate recommendation
    updated_dec = service.generate_recommendation(
        "DEC-ELIG-01",
        [cand_pass, cand_fail, cand_unknown, cand_conflicted],
        raw_matrix,
    )

    assert updated_dec.status == DecisionStatus.RECOMMENDED
    assert updated_dec.selected_candidate == "TPS62130"
    # Ineligible candidates must not be in alternatives
    assert "BadReg" not in updated_dec.alternatives
    assert "ConflictReg" not in updated_dec.alternatives
