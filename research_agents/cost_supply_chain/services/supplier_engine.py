"""
Multi-criteria supplier candidate evaluation, scoring, and ranking engine.
"""

from typing import List, Optional
from research_agents.cost_supply_chain.schemas import (
    SupplierCandidate,
    SupplierComparison,
    VerificationStatus,
)


class SupplierEngine:
    """Evaluates and ranks supplier candidates for engineering parts."""

    def evaluate_suppliers(
        self,
        part_id: str,
        candidates: List[SupplierCandidate],
        target_volume: int = 1000,
        max_acceptable_lead_time: float = 16.0,
    ) -> SupplierComparison:
        if not candidates:
            return SupplierComparison(
                part_id=part_id,
                candidates=[],
                recommended_supplier_id=None,
                recommendation_rationale="No candidate suppliers available for evaluation.",
            )

        scored = []
        valid_prices = [c.unit_price for c in candidates if c.unit_price is not None]
        min_price = min(valid_prices) if valid_prices else 1.0

        for cand in candidates:
            score = 0.0
            reasons = []

            if cand.unit_price is not None and cand.unit_price > 0:
                cost_score = min(1.0, min_price / cand.unit_price) * 40.0
                score += cost_score
            else:
                score += 10.0

            if cand.lead_time_weeks is not None:
                if cand.lead_time_weeks <= max_acceptable_lead_time:
                    lt_score = (1.0 - (cand.lead_time_weeks / (max_acceptable_lead_time * 1.5))) * 25.0
                    score += max(5.0, lt_score)
                else:
                    score += 5.0
                    reasons.append(f"Long lead time ({cand.lead_time_weeks} wks)")
            else:
                score += 10.0

            if cand.verification_status == VerificationStatus.VERIFIED:
                score += 15.0
            elif cand.verification_status == VerificationStatus.CLAIMED:
                score += 8.0
            else:
                score += 3.0

            if any("ISO 9001" in c.upper() or "AS9100" in c.upper() for c in cand.certifications):
                score += 5.0

            if cand.moq is not None:
                if cand.moq <= target_volume:
                    score += 15.0
                elif cand.moq <= target_volume * 2:
                    score += 8.0
                    reasons.append(f"Elevated MOQ ({cand.moq} vs batch {target_volume})")
                else:
                    score += 2.0
                    reasons.append(f"Prohibitive MOQ ({cand.moq} vs batch {target_volume})")
            else:
                score += 8.0

            scored.append((round(score, 2), cand, "; ".join(reasons)))

        scored.sort(key=lambda x: x[0], reverse=True)
        top_score, top_cand, flags = scored[0]

        rationale = (
            f"Recommended supplier {top_cand.name} (Score: {top_score}/100) based on unit cost of "
            f"{top_cand.unit_price or 'N/A'} {top_cand.currency}, lead time of {top_cand.lead_time_weeks or 'N/A'} weeks, "
            f"and verification status '{top_cand.verification_status.value}'."
        )
        if flags:
            rationale += f" Note risks: {flags}."

        return SupplierComparison(
            part_id=part_id,
            candidates=[item[1] for item in scored],
            recommended_supplier_id=top_cand.supplier_id,
            recommendation_rationale=rationale,
        )
