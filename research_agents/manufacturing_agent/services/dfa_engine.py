"""
Core Design-for-Assembly (DFA) Analysis Engine (Section 2).
"""

from typing import Any, Dict, List, Optional
from research_agents.manufacturing_agent.schemas import DFAFinding, DFAModel


class DFAEngine:
    """Evaluates assembly complexity, part consolidation, fastener count, and poka-yoke error-proofing."""

    def analyze_assembly(
        self,
        assembly: Dict[str, Any],
    ) -> DFAModel:
        aid = assembly.get("assembly_id", "MAIN_ASSEMBLY")
        parts = assembly.get("part_count", 1)
        fasteners = assembly.get("fastener_count", 0)
        unique_fasteners = assembly.get("unique_fastener_types", 1)
        findings: List[DFAFinding] = []

        # 1. Excessive fastener count
        if fasteners > 10:
            findings.append(
                DFAFinding(
                    finding_id=f"DFA-FAST-{aid}",
                    assembly_id=aid,
                    category="FASTENER_COUNT",
                    severity="MAJOR",
                    description=f"Assembly contains {fasteners} threaded fasteners.",
                    rationale="High fastener count increases assembly labor, tool changeovers, and missing screw risk.",
                    evidence_level="E3",
                )
            )

        # 2. Too many unique fastener sizes/types
        if unique_fasteners > 3:
            findings.append(
                DFAFinding(
                    finding_id=f"DFA-TOOL-{aid}",
                    assembly_id=aid,
                    category="TOOL_CLEARANCE",
                    severity="MINOR",
                    description=f"Assembly requires {unique_fasteners} distinct fastener types, requiring multiple driver bits.",
                    rationale="Standardizing fastener heads reduces assembly line tool swapping.",
                    evidence_level="E2",
                )
            )

        # 3. Orientation ambiguity / lack of poka-yoke
        if assembly.get("orientation_ambiguity", False) or assembly.get("near_symmetric", False):
            findings.append(
                DFAFinding(
                    finding_id=f"DFA-POKA-{aid}",
                    assembly_id=aid,
                    category="ORIENTATION_AMBIGUITY",
                    severity="CRITICAL",
                    description="Near-symmetric mating flange allows 180-degree inverted installation.",
                    rationale="Operator cannot immediately visually distinguish correct orientation during blind insertion.",
                    proposed_poka_yoke="Add locating dowel pin or offset one mounting bolt hole by 5mm.",
                    evidence_level="E3",
                )
            )

        # 4. Insertion access / direction
        directions = assembly.get("insertion_directions", ["Z"])
        if len(directions) > 2:
            findings.append(
                DFAFinding(
                    finding_id=f"DFA-DIR-{aid}",
                    assembly_id=aid,
                    category="INSERTION_ACCESS",
                    severity="MAJOR",
                    description=f"Assembly requires multi-axis insertions across {len(directions)} axes ({', '.join(directions)}).",
                    rationale="Unidirectional (top-down Z) assembly significantly lowers fixturing cost and enables robotic automation.",
                    evidence_level="E3",
                )
            )

        # Calculate poka-yoke and DFA score
        poka_score = 10.0 - (len([f for f in findings if f.severity in ("CRITICAL", "BLOCKER")]) * 3.0 + len(findings) * 0.5)
        poka_score = max(0.0, min(10.0, poka_score))

        return DFAModel(
            assembly_id=aid,
            total_part_count=parts,
            total_fastener_count=fasteners,
            unique_fastener_types=unique_fasteners,
            estimated_assembly_steps=parts + fasteners,
            poka_yoke_score=round(poka_score, 1),
            findings=findings,
        )
