"""
Design Improvement Recommendations & Cost Driver Exporter (Sections 13 & 14).
"""

from typing import Any, Dict, List
from research_agents.manufacturing_agent.schemas import (
    CostDriverHandoff,
    DFAFinding,
    DFMFinding,
    ManufacturingRecommendation,
)


class RecommendationEngine:
    """Transforms DFM/DFA findings into formal design change proposals and cost drivers for Agent #25."""

    def generate_recommendations(
        self,
        dfm_findings: List[DFMFinding],
        dfa_findings: List[DFAFinding],
    ) -> List[ManufacturingRecommendation]:
        recs: List[ManufacturingRecommendation] = []

        for f in dfm_findings:
            recs.append(
                ManufacturingRecommendation(
                    recommendation_id=f"REC-{f.finding_id}",
                    finding_id=f.finding_id,
                    component_id=f.component_id,
                    current_condition=f.description,
                    proposed_change=f"Optimize geometry or tooling to resolve {f.category.lower().replace('_', ' ')}.",
                    engineering_rationale=f.rationale or "Improves tool life, reduces cycle time, and avoids machining bottlenecks.",
                    expected_manufacturing_impact="Lowers scrap rate and improves manufacturing yield.",
                    expected_assembly_impact="Neutral on assembly operations.",
                    possible_engineering_tradeoffs="May require minor feature envelope adjustment.",
                    confidence=0.92,
                    evidence_level=f.evidence_level,
                    change_request_id=f"CHG-MFG-{f.component_id}",
                )
            )

        for d in dfa_findings:
            recs.append(
                ManufacturingRecommendation(
                    recommendation_id=f"REC-{d.finding_id}",
                    finding_id=d.finding_id,
                    component_id=d.affected_component_ids[0] if d.affected_component_ids else "ASSEMBLY_CHASSIS",
                    current_condition=d.description,
                    proposed_change=d.proposed_poka_yoke or "Standardize fasteners or consolidate mating components.",
                    engineering_rationale=d.rationale or "Reduces assembly cycle time and eliminates human error.",
                    expected_manufacturing_impact="Neutral on fabrication.",
                    expected_assembly_impact="Directly decreases assembly duration and eliminates rework.",
                    possible_engineering_tradeoffs="May increase tooling complexity if molded.",
                    confidence=0.95,
                    evidence_level=d.evidence_level,
                    change_request_id=f"CHG-DFA-{d.finding_id}",
                )
            )

        return recs

    def build_cost_drivers(
        self,
        project_id: str,
        components: List[Dict[str, Any]],
        dfm_findings: List[DFMFinding],
    ) -> List[CostDriverHandoff]:
        drivers: List[CostDriverHandoff] = []
        for c in components:
            cid = c.get("component_id", "COMP-001")
            proc = str(c.get("intended_process", "CNC_MACHINING")).upper()
            related_dfm = [f for f in dfm_findings if f.component_id == cid]

            setups = 2 if any(f.category == "FEATURE_ACCESSIBILITY" for f in related_dfm) else 1
            tol_diff = "TIGHT / DIFFICULT" if any(f.category == "TOLERANCE_DIFFICULTY" for f in related_dfm) else "STANDARD"

            drivers.append(
                CostDriverHandoff(
                    project_id=project_id,
                    component_id=cid,
                    process_family=proc,
                    part_count_impact="1 unit per assembly",
                    setup_count_estimate=setups,
                    tooling_complexity="HIGH" if "MOLD" in proc else "LOW",
                    tolerance_difficulty=tol_diff,
                    inspection_burden="HIGH" if tol_diff == "TIGHT / DIFFICULT" else "STANDARD",
                    automation_potential="HIGH",
                )
            )
        return drivers
