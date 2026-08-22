"""Engineering Design Decision Service."""

import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.decision.models import (
    CriterionCategory,
    CriterionDirection,
    DecisionCandidate,
    DecisionCriterion,
    DecisionStatus,
    DecisionTradeoff,
    DecisionType,
    EngineeringDecision,
)
from backend.workline.decision.scoring import DeterministicScorer
from backend.workline.decision.sensitivity import SensitivityAnalyzer
from backend.workline.decision.tradeoffs import TradeoffEngine
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions


class DecisionService:
    """Service managing design decision lifecycles, ranking, and human approvals."""

    def __init__(self):
        self._lock = threading.RLock()
        self._decisions: Dict[str, EngineeringDecision] = {}
        self._history: Dict[str, List[EngineeringDecision]] = {}

    def create_decision(
        self,
        decision_id: str,
        project_id: str,
        title: str,
        description: str,
        decision_type: DecisionType = DecisionType.COMPONENT_SELECTION,
        criteria: Optional[List[DecisionCriterion]] = None,
        team_id: str = "default_team",
        created_by: str = "engineer",
    ) -> EngineeringDecision:
        with self._lock:
            # Default criteria if none provided
            if not criteria:
                criteria = [
                    DecisionCriterion(criterion_id="crit_tech", name="Technical Fit", category=CriterionCategory.TECHNICAL_FIT, weight=0.40, direction=CriterionDirection.MAXIMIZE, mandatory=True),
                    DecisionCriterion(criterion_id="crit_cost", name="Unit Cost", category=CriterionCategory.COST, weight=0.20, direction=CriterionDirection.MINIMIZE),
                    DecisionCriterion(criterion_id="crit_avail", name="Supplier Availability", category=CriterionCategory.AVAILABILITY, weight=0.20, direction=CriterionDirection.MAXIMIZE),
                    DecisionCriterion(criterion_id="crit_risk", name="Supply Chain Risk", category=CriterionCategory.RISK, weight=0.20, direction=CriterionDirection.MINIMIZE),
                ]

            dec = EngineeringDecision(
                decision_id=decision_id,
                project_id=project_id,
                team_id=team_id,
                title=title,
                description=description,
                status=DecisionStatus.DRAFT,
                decision_type=decision_type,
                criteria=criteria,
                created_by=created_by,
                version=1,
                created_at=time.time(),
                updated_at=time.time(),
            )
            self._decisions[decision_id] = dec
            self._history[decision_id] = [dec]
            return dec

    def get_decision(self, decision_id: str) -> Optional[EngineeringDecision]:
        with self._lock:
            return self._decisions.get(decision_id)

    def list_decisions(self, project_id: Optional[str] = None) -> List[EngineeringDecision]:
        with self._lock:
            if project_id:
                return [d for d in self._decisions.values() if d.project_id == project_id]
            return list(self._decisions.values())

    def generate_recommendation(
        self,
        decision_id: str,
        candidates: List[DecisionCandidate],
        raw_matrix: Dict[str, Dict[str, float]],
    ) -> EngineeringDecision:
        with self._lock:
            dec = self._decisions.get(decision_id)
            if not dec:
                raise ValueError(f"Decision '{decision_id}' not found.")

            # Filter eligible candidates
            eligible = [c for c in candidates if c.eligibility_status == "ELIGIBLE"]
            if not eligible:
                dec.status = DecisionStatus.UNDER_REVIEW
                dec.recommendation = "No eligible candidates found passing all mandatory requirements."
                dec.rationale = "Mandatory constraints failed or conflicted across all candidates."
                return dec

            # Score each candidate
            scored_candidates = []
            for c in eligible:
                score, crit_scores = DeterministicScorer.calculate_score(c, dec.criteria, raw_matrix.get(c.candidate_id, {}))
                c.score = score
                c.criterion_scores = crit_scores
                scored_candidates.append(c)

            scored_candidates.sort(key=lambda x: x.score, reverse=True)
            winner = scored_candidates[0]
            alternatives = [c.name for c in scored_candidates[1:]]

            # Sensitivity Analysis
            stability, _ = SensitivityAnalyzer.analyze(scored_candidates, dec.criteria, raw_matrix)

            dec.status = DecisionStatus.RECOMMENDED
            dec.selected_candidate = winner.name
            dec.alternatives = alternatives
            dec.recommendation = f"Recommend '{winner.name}' with multi-criteria score of {winner.score}."
            dec.rationale = f"Selected '{winner.name}' based on superior technical fit and acceptable risk."
            dec.stability = stability
            dec.confidence = winner.score
            dec.updated_at = time.time()

            return dec

    def approve_decision(
        self,
        decision_id: str,
        approved_by: str,
        role: str = "ENGINEER",
    ) -> EngineeringDecision:
        with self._lock:
            dec = self._decisions.get(decision_id)
            if not dec:
                raise ValueError(f"Decision '{decision_id}' not found.")

            dec.status = DecisionStatus.APPROVED
            dec.approved_by = f"{approved_by} ({role})"
            dec.approved_at = time.time()
            dec.updated_at = time.time()
            return dec

    def reject_decision(
        self,
        decision_id: str,
        rejected_by: str,
        reason: str,
    ) -> EngineeringDecision:
        with self._lock:
            dec = self._decisions.get(decision_id)
            if not dec:
                raise ValueError(f"Decision '{decision_id}' not found.")

            dec.status = DecisionStatus.REJECTED
            dec.rationale = f"Rejected by {rejected_by}: {reason}"
            dec.updated_at = time.time()
            return dec

    def supersede_decision(
        self,
        old_decision_id: str,
        new_decision_id: str,
    ) -> EngineeringDecision:
        with self._lock:
            old_dec = self._decisions.get(old_decision_id)
            if not old_dec:
                raise ValueError(f"Old decision '{old_decision_id}' not found.")

            old_dec.status = DecisionStatus.SUPERSEDED
            old_dec.superseded_by = new_decision_id
            old_dec.updated_at = time.time()
            return old_dec

    def get_history(self, decision_id: str) -> List[EngineeringDecision]:
        with self._lock:
            return self._history.get(decision_id, [])


# Global singleton instance
decision_service = DecisionService()
