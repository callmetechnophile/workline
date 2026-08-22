"""Deterministic multi-criteria scoring and normalization engine."""

from typing import Dict, List, Optional, Tuple
from backend.workline.decision.models import (
    CriterionDirection,
    DecisionCandidate,
    DecisionCriterion,
)


class DeterministicScorer:
    """Scores candidate options against explicit criteria."""

    @classmethod
    def calculate_score(
        cls,
        candidate: DecisionCandidate,
        criteria: List[DecisionCriterion],
        raw_values: Dict[str, Optional[float]],
        policy: str = "CONSERVATIVE",
    ) -> Tuple[float, Dict[str, float]]:
        total_score = 0.0
        total_weight = 0.0
        scores: Dict[str, float] = {}

        for crit in criteria:
            val = raw_values.get(crit.criterion_id)
            score = 0.0

            if val is None:
                if policy == "STRICT":
                    score = 0.0
                elif policy == "CONSERVATIVE":
                    score = 0.2  # Penalize missing specification
                else:
                    continue  # NEUTRAL: skip from weighted average
            else:
                if crit.direction == CriterionDirection.MAXIMIZE:
                    score = min(max(val, 0.0), 1.0)
                elif crit.direction == CriterionDirection.MINIMIZE:
                    score = max(0.0, 1.0 - min(val, 1.0))
                elif crit.direction == CriterionDirection.TARGET and crit.target_value is not None:
                    diff = abs(val - crit.target_value)
                    denom = crit.target_value if crit.target_value > 0 else 1.0
                    score = max(0.0, 1.0 - (diff / denom))
                else:
                    score = min(max(val, 0.0), 1.0)

            scores[crit.criterion_id] = round(score, 3)
            total_score += score * crit.weight
            total_weight += crit.weight

        final_score = round(total_score / total_weight, 4) if total_weight > 0 else 0.0
        return final_score, scores
