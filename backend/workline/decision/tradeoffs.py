"""Trade-off analysis engine for decision support."""

from typing import List
from backend.workline.decision.models import (
    DecisionCandidate,
    DecisionCriterion,
    DecisionTradeoff,
)


class TradeoffEngine:
    """Calculates trade-offs between candidate engineering choices."""

    @classmethod
    def compare_pair(
        cls,
        candidate_a: DecisionCandidate,
        candidate_b: DecisionCandidate,
        criteria: List[DecisionCriterion],
    ) -> List[DecisionTradeoff]:
        tradeoffs: List[DecisionTradeoff] = []

        for crit in criteria:
            score_a = candidate_a.criterion_scores.get(crit.criterion_id, 0.0)
            score_b = candidate_b.criterion_scores.get(crit.criterion_id, 0.0)
            diff = score_a - score_b

            if abs(diff) > 0.05:
                tradeoffs.append(
                    DecisionTradeoff(
                        candidate_a=candidate_a.name,
                        candidate_b=candidate_b.name,
                        criterion=crit.name,
                        advantage_candidate=candidate_a.name if diff > 0 else candidate_b.name,
                        disadvantage_candidate=candidate_b.name if diff > 0 else candidate_a.name,
                        score_delta=round(abs(diff), 3),
                    )
                )

        return tradeoffs
