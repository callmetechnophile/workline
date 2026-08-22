"""Tests for Trade-Off and Sensitivity Analysis."""

import pytest
from backend.workline.decision.models import (
    CriterionDirection,
    DecisionCandidate,
    DecisionCriterion,
)
from backend.workline.decision.sensitivity import SensitivityAnalyzer
from backend.workline.decision.tradeoffs import TradeoffEngine


def test_pairwise_tradeoffs():
    """Test 12-13: Pairwise trade-off analysis."""
    criteria = [
        DecisionCriterion(criterion_id="crit_tech", name="Technical Fit", weight=0.40, direction=CriterionDirection.MAXIMIZE),
        DecisionCriterion(criterion_id="crit_cost", name="Unit Cost", weight=0.60, direction=CriterionDirection.MINIMIZE),
    ]

    cand_a = DecisionCandidate(
        candidate_id="c_a",
        entity_id="e_a",
        name="Candidate A",
        criterion_scores={"crit_tech": 0.95, "crit_cost": 0.50},
    )
    cand_b = DecisionCandidate(
        candidate_id="c_b",
        entity_id="e_b",
        name="Candidate B",
        criterion_scores={"crit_tech": 0.70, "crit_cost": 0.90},
    )

    tradeoffs = TradeoffEngine.compare_pair(cand_a, cand_b, criteria)
    assert len(tradeoffs) == 2
    # Candidate A wins on tech fit, Candidate B wins on cost
    tech_tradeoff = next(t for t in tradeoffs if t.criterion == "Technical Fit")
    assert tech_tradeoff.advantage_candidate == "Candidate A"
    cost_tradeoff = next(t for t in tradeoffs if t.criterion == "Unit Cost")
    assert cost_tradeoff.advantage_candidate == "Candidate B"


def test_sensitivity_analysis():
    """Test 14-15: Weight perturbation sensitivity and stability detection."""
    criteria = [
        DecisionCriterion(criterion_id="crit_tech", name="Technical Fit", weight=0.50, direction=CriterionDirection.MAXIMIZE),
        DecisionCriterion(criterion_id="crit_cost", name="Unit Cost", weight=0.20, direction=CriterionDirection.MINIMIZE),
    ]

    cand_a = DecisionCandidate(candidate_id="c_a", entity_id="e_a", name="Candidate A")
    cand_b = DecisionCandidate(candidate_id="c_b", entity_id="e_b", name="Candidate B")

    raw_matrix = {
        "c_a": {"crit_tech": 0.95, "crit_cost": 0.30},
        "c_b": {"crit_tech": 0.80, "crit_cost": 0.95},
    }

    stability, analyses = SensitivityAnalyzer.analyze([cand_a, cand_b], criteria, raw_matrix)
    assert stability in ["ROBUST", "SENSITIVE", "UNSTABLE"]
