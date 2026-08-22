"""Sensitivity Analysis for Decision Criteria Weight Perturbations."""

from typing import Dict, List, Tuple
from backend.workline.decision.models import (
    DecisionCandidate,
    DecisionCriterion,
    SensitivityAnalysis,
)
from backend.workline.decision.scoring import DeterministicScorer


class SensitivityAnalyzer:
    """Evaluates stability of the top recommendation against weight variations."""

    @classmethod
    def analyze(
        cls,
        candidates: List[DecisionCandidate],
        criteria: List[DecisionCriterion],
        raw_matrix: Dict[str, Dict[str, float]],
    ) -> Tuple[str, List[SensitivityAnalysis]]:
        if len(candidates) < 2:
            return "ROBUST", []

        # Find base winner
        scored_base = []
        for c in candidates:
            score, _ = DeterministicScorer.calculate_score(c, criteria, raw_matrix.get(c.candidate_id, {}))
            scored_base.append((c.name, score))
        scored_base.sort(key=lambda x: x[1], reverse=True)
        base_winner = scored_base[0][0]

        analyses: List[SensitivityAnalysis] = []
        rank_changes = 0

        for crit in criteria:
            for factor in [0.5, 1.5, 2.0]:
                perturbed_criteria = [
                    crit.model_copy(update={"weight": crit.weight * factor})
                    if c.criterion_id == crit.criterion_id
                    else c
                    for c in criteria
                ]

                scored_perturbed = []
                for c in candidates:
                    score, _ = DeterministicScorer.calculate_score(c, perturbed_criteria, raw_matrix.get(c.candidate_id, {}))
                    scored_perturbed.append((c.name, score))
                scored_perturbed.sort(key=lambda x: x[1], reverse=True)
                new_winner = scored_perturbed[0][0]

                if new_winner != base_winner:
                    rank_changes += 1
                    analyses.append(
                        SensitivityAnalysis(
                            criterion_id=crit.criterion_id,
                            original_weight=crit.weight,
                            tested_weight=round(crit.weight * factor, 2),
                            original_winner=base_winner,
                            new_winner=new_winner,
                            is_ranking_changed=True,
                        )
                    )

        stability = "ROBUST"
        if rank_changes >= 3:
            stability = "UNSTABLE"
        elif rank_changes > 0:
            stability = "SENSITIVE"

        return stability, analyses
