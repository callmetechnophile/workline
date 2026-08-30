"""
Engineering decision and recommendation engine for EngineeringSynthesisAgent (Sections 8, 9, 11, 12, 23).
Generates traceable design decisions, recommendations, assumptions, and unknowns.
"""

from typing import List, Tuple
from research_agents.engineering_synthesis_agent.schemas import (
    AssumptionItem,
    EngineeringDecision,
    EngineeringTradeoff,
    ProjectMeta,
    RecommendationItem,
    RequirementAnalysis,
    TechnicalFinding,
    UnknownItem,
)


class DecisionEngine:
    """Formulates concrete engineering decisions, recommendations, assumptions, and unknowns."""

    def generate_decisions_and_recommendations(
        self,
        project: ProjectMeta,
        requirements: List[RequirementAnalysis],
        findings: List[TechnicalFinding],
        tradeoffs: List[EngineeringTradeoff],
    ) -> Tuple[List[EngineeringDecision], List[RecommendationItem], List[AssumptionItem], List[UnknownItem]]:
        """
        Synthesizes decisions and recommendations based on trade-offs and project requirements.
        """
        decisions: List[EngineeringDecision] = []
        recommendations: List[RecommendationItem] = []
        assumptions: List[AssumptionItem] = []
        unknowns: List[UnknownItem] = []

        req_ids = [r.requirement_id for r in requirements]

        # 1. Decisions derived from Trade-offs
        for idx, trade in enumerate(tradeoffs, 1):
            dec_id = f"DEC-{idx:03d}"
            alts = [opt.option for opt in trade.options if opt.option != trade.recommended_option]
            all_ev = [eid for opt in trade.options for eid in opt.evidence_ids]

            decisions.append(
                EngineeringDecision(
                    decision_id=dec_id,
                    decision_area=trade.decision_area,
                    selected_option=trade.recommended_option,
                    alternatives=alts,
                    decision_reason=trade.reasoning,
                    tradeoffs=[trade.tradeoff_id],
                    evidence_ids=list(set(all_ev)),
                    requirement_ids=req_ids[:2],
                    confidence=trade.confidence,
                    validation_required=True,
                )
            )

        # 2. Recommendations
        rec_id = "REC-001"
        if decisions:
            top_dec = decisions[0]
            recommendations.append(
                RecommendationItem(
                    recommendation_id=rec_id,
                    category="architecture",
                    recommendation=f"Adopt `{top_dec.selected_option}` as the baseline for {top_dec.decision_area}.",
                    reason=top_dec.decision_reason,
                    supporting_evidence_ids=top_dec.evidence_ids,
                    supporting_requirement_ids=top_dec.requirement_ids,
                    assumptions=["Payload power budget is sufficient."],
                    confidence=top_dec.confidence,
                    validation_required=True,
                )
            )

        recommendations.append(
            RecommendationItem(
                recommendation_id=f"REC-{len(recommendations)+1:03d}",
                category="power",
                recommendation="Design dedicated DC-DC step-down switching stages with >= 20% current headroom.",
                reason="Prevents transient voltage drops and compute brownouts during burst neural inference.",
                supporting_evidence_ids=[],
                supporting_requirement_ids=req_ids[:1],
                assumptions=["Supply voltage exceeds 12V LiPo."],
                confidence=0.92,
                validation_required=True,
            )
        )

        # 3. Explicit Assumptions (Section 11)
        assumptions.append(
            AssumptionItem(
                assumption_id="ASM-001",
                assumption="The operating ambient temperature stays within -10 deg C to +45 deg C during mission flights.",
                impact="Dictates heatsink sizing and battery discharge chemistry.",
                confidence=0.85,
                validation_required=True,
            )
        )

        # 4. Unknowns / Missing Information (Section 12)
        unknowns.append(
            UnknownItem(
                unknown_id="UNK-001",
                unknown="Exact optical transmission loss of thermal lens in dense fog / smoke conditions.",
                why_it_matters="Affects minimum altitude and sensor detection distance thresholds.",
                required_information="Empirical field measurement or chamber smoke attenuation data.",
                blocking=False,
            )
        )

        return decisions, recommendations, assumptions, unknowns
