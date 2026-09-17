"""
Manufacturing Tooling and Fixture Analysis Engine (Section 6).
"""

from typing import Any, Dict, List
from research_agents.manufacturing_agent.schemas import ToolingRequirement


class ToolingEngine:
    """Identifies jigs, fixtures, molds, soft jaws, and tooling requirements."""

    def evaluate_tooling(
        self,
        components: List[Dict[str, Any]],
    ) -> List[ToolingRequirement]:
        tooling: List[ToolingRequirement] = []
        for c in components:
            cid = c.get("component_id", "COMP-001")
            proc = str(c.get("intended_process", "CNC_MACHINING")).upper()

            if "INJECTION_MOLDING" in proc:
                tooling.append(
                    ToolingRequirement(
                        tooling_id=f"TOOL-MOLD-{cid}",
                        name=f"Multi-Cavity Hardened Steel Injection Mold for {cid}",
                        type="MOLD",
                        necessity="MANDATORY",
                        complexity="HIGH",
                        reuse_potential="PROJECT_DEDICATED",
                        associated_component_ids=[cid],
                        description="P20/H13 tool steel injection mold with core/cavity inserts, cooling channels, and ejector pins.",
                    )
                )

            elif "CNC" in proc:
                tooling.append(
                    ToolingRequirement(
                        tooling_id=f"TOOL-JAWS-{cid}",
                        name=f"Custom Machined Soft Jaws for {cid}",
                        type="SOFT_JAWS",
                        necessity="RECOMMENDED",
                        complexity="LOW",
                        reuse_potential="REUSABLE_MODULAR",
                        associated_component_ids=[cid],
                        description="Aluminum soft jaws contour-matched to part profile for 2nd operation flip setup.",
                    )
                )

            elif "SHEET_METAL" in proc:
                tooling.append(
                    ToolingRequirement(
                        tooling_id=f"TOOL-DIE-{cid}",
                        name=f"Standard V-Die and Punch Tooling for {cid}",
                        type="DIE",
                        necessity="MANDATORY",
                        complexity="LOW",
                        reuse_potential="STANDARD_CATALOG",
                        associated_component_ids=[cid],
                        description="Air bending standard 88-degree punch and V-die set.",
                    )
                )

        return tooling
