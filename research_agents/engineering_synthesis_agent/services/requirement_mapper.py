"""
Requirement mapping and qualitative coverage evaluation service for EngineeringSynthesisAgent.
Maps project requirements to evidence and technical findings (Section 4 & Section 16).
"""

from typing import Any, Dict, List
from research_agents.engineering_synthesis_agent.schemas import (
    ProjectMeta,
    RequirementAnalysis,
    RequirementCoverageLiteral,
)


class RequirementMapper:
    """Maps project requirements to evidence and computes qualitative coverage."""

    def map_requirements(
        self,
        project: ProjectMeta,
        evidence_items: List[Dict[str, Any]],
        technical_finding_ids: List[str],
    ) -> List[RequirementAnalysis]:
        """
        Analyzes project requirements against gathered research evidence.
        """
        analyses: List[RequirementAnalysis] = []
        req_list = project.requirements or project.objectives

        if not req_list:
            req_list = [f"Satisfy overall objectives of {project.title}"]

        for idx, req_text in enumerate(req_list, 1):
            req_id = f"REQ-{idx:03d}"
            req_lower = req_text.lower()

            # Find matching evidence
            matching_ev_ids: List[str] = []
            for ev in evidence_items:
                ev_text = (ev.get("text") or ev.get("abstract") or ev.get("description") or "").lower()
                ev_title = (ev.get("title") or "").lower()

                # Keyword overlap
                tokens = [t for t in req_lower.split() if len(t) > 3]
                if any(tok in ev_text or tok in ev_title for tok in tokens):
                    eid = ev.get("evidence_id") or ev.get("source_id") or f"ev_{len(matching_ev_ids)+1}"
                    matching_ev_ids.append(eid)

            ev_count = len(matching_ev_ids)

            # Determine qualitative coverage
            coverage: RequirementCoverageLiteral
            if ev_count >= 2:
                coverage = "strong"
            elif ev_count == 1:
                coverage = "partial"
            elif ev_count == 0 and evidence_items:
                coverage = "weak"
            else:
                coverage = "unsupported"

            confidence = 0.95 if coverage == "strong" else (0.80 if coverage == "partial" else 0.60)

            analyses.append(
                RequirementAnalysis(
                    requirement_id=req_id,
                    requirement=req_text,
                    coverage=coverage,
                    evidence_count=ev_count,
                    supporting_evidence_ids=matching_ev_ids[:5],
                    technical_findings=technical_finding_ids[:2],
                    decision_available=coverage in ("strong", "partial"),
                    confidence=confidence,
                )
            )

        return analyses
