"""Tests for Deterministic Scoring, Normalization, and Uncertainty Policies."""

import pytest
from backend.workline.decision.models import (
    CriterionCategory,
    CriterionDirection,
    DecisionCandidate,
    DecisionCriterion,
)
from backend.workline.decision.scoring import DeterministicScorer


def test_deterministic_weighted_scoring():
    """Test 5-8: Multi-criteria weighted scoring."""
    criteria = [
        DecisionCriterion(criterion_id="crit_tech", name="Technical Fit", weight=0.50, direction=CriterionDirection.MAXIMIZE),
        DecisionCriterion(criterion_id="crit_cost", name="Unit Cost", weight=0.20, direction=CriterionDirection.MINIMIZE),
        DecisionCriterion(criterion_id="crit_avail", name="Availability", weight=0.15, direction=CriterionDirection.MAXIMIZE),
        DecisionCriterion(criterion_id="crit_risk", name="Risk", weight=0.15, direction=CriterionDirection.MINIMIZE),
    ]

    cand_a = DecisionCandidate(candidate_id="c_a", entity_id="e_a", name="Candidate A")
    cand_b = DecisionCandidate(candidate_id="c_b", entity_id="e_b", name="Candidate B")

    # Candidate A: high tech fit, higher cost
    raw_a = {"crit_tech": 0.95, "crit_cost": 0.30, "crit_avail": 0.90, "crit_risk": 0.10}
    # Candidate B: lower tech fit, lower cost
    raw_b = {"crit_tech": 0.80, "crit_cost": 0.10, "crit_avail": 0.80, "crit_risk": 0.30}

    score_a, crit_scores_a = DeterministicScorer.calculate_score(cand_a, criteria, raw_a)
    score_b, crit_scores_b = DeterministicScorer.calculate_score(cand_b, criteria, raw_b)

    assert score_a > score_b
    assert isinstance(score_a, float)
    assert "crit_tech" in crit_scores_a


def test_uncertainty_policies():
    """Test 9-11: STRICT, CONSERVATIVE, and NEUTRAL uncertainty policies."""
    criteria = [
        DecisionCriterion(criterion_id="crit_tech", name="Technical Fit", weight=0.50, direction=CriterionDirection.MAXIMIZE),
        DecisionCriterion(criterion_id="crit_cost", name="Unit Cost", weight=0.50, direction=CriterionDirection.MINIMIZE),
    ]

    cand = DecisionCandidate(candidate_id="c_unk", entity_id="e_unk", name="Candidate Unknown")
    raw_missing = {"crit_tech": 0.90, "crit_cost": None}

    # Strict: missing cost treated as 0
    score_strict, _ = DeterministicScorer.calculate_score(cand, criteria, raw_missing, policy="STRICT")
    assert score_strict == pytest.approx(0.45, 0.01)

    # Conservative: missing cost penalized
    score_cons, _ = DeterministicScorer.calculate_score(cand, criteria, raw_missing, policy="CONSERVATIVE")
    assert score_cons == pytest.approx(0.55, 0.01)

    # Neutral: missing cost excluded
    score_neut, _ = DeterministicScorer.calculate_score(cand, criteria, raw_missing, policy="NEUTRAL")
    assert score_neut == pytest.approx(0.90, 0.01)
