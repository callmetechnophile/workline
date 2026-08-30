"""
Technical finding extraction service for EngineeringSynthesisAgent.
Transforms deep research outputs and verified claims into structured project-specific findings (Section 5).
"""

from typing import Any, Dict, List
from research_agents.engineering_synthesis_agent.schemas import TechnicalFinding


class FindingExtractor:
    """Extracts project-relevant technical findings while preserving evidence provenance."""

    def extract_findings(
        self,
        deep_research_data: Dict[str, Any],
        raw_facts: List[Dict[str, Any]],
        evidence_items: List[Dict[str, Any]],
    ) -> List[TechnicalFinding]:
        """
        Extracts structured technical findings from Agent #4 deep research and processed facts.
        """
        findings: List[TechnicalFinding] = []
        counter = 0

        # 1. Ingest claims from Deep Research (Agent #4)
        claims = deep_research_data.get("extracted_claims") or []
        for c in claims:
            counter += 1
            claim_text = c.get("claim", "")
            ev_ids = c.get("source_evidence_ids", [])
            category = "compute" if any(k in claim_text.lower() for k in ["tops", "fps", "compute", "gpu"]) else "architecture"
            if "power" in claim_text.lower() or "watt" in claim_text.lower():
                category = "power"
            elif "thermal" in claim_text.lower() or "temperature" in claim_text.lower():
                category = "thermal"

            findings.append(
                TechnicalFinding(
                    finding_id=f"FIND-{counter:03d}",
                    category=category,
                    finding=claim_text,
                    evidence_ids=ev_ids,
                    impact_on_project=f"Directly influences {category} architecture and component sizing.",
                    confidence=float(c.get("confidence", 0.90)),
                )
            )

        # 2. Ingest engineering implications from Agent #4
        implications = deep_research_data.get("engineering_implications") or []
        for imp in implications:
            counter += 1
            findings.append(
                TechnicalFinding(
                    finding_id=f"FIND-{counter:03d}",
                    category=imp.get("category", "architecture"),
                    finding=imp.get("finding", ""),
                    evidence_ids=[],
                    impact_on_project=imp.get("impact_on_project", "Shapes hardware and firmware requirements."),
                    confidence=0.92,
                )
            )

        # 3. Fallback to raw facts if no deep research
        if not findings and raw_facts:
            for f in raw_facts[:5]:
                counter += 1
                f_text = f.get("fact", "")
                findings.append(
                    TechnicalFinding(
                        finding_id=f"FIND-{counter:03d}",
                        category="hardware",
                        finding=f_text,
                        evidence_ids=[f.get("source_document") or f"fact_{counter}"],
                        impact_on_project="Informs component interface compatibility.",
                        confidence=float(f.get("confidence", 0.90)),
                    )
                )

        return findings
