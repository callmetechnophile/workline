"""
Core Design-for-Manufacturing (DFM) Analysis Engine (Section 1).
"""

from typing import Any, Dict, List, Optional
from research_agents.manufacturing_agent.schemas import DFMFinding


class DFMEngine:
    """Evaluates component design features against manufacturing process capabilities."""

    def analyze_component(
        self,
        component: Dict[str, Any],
    ) -> List[DFMFinding]:
        findings: List[DFMFinding] = []
        cid = component.get("component_id", "COMP-001")
        proc = str(component.get("intended_process", "CNC_MACHINING")).upper()
        mat = str(component.get("material", "ALUMINUM_6061")).upper()

        # Rule 1: Cavity aspect ratio / Feature accessibility (Milling)
        depth = component.get("pocket_depth_mm", 0.0)
        radius = component.get("pocket_corner_radius_mm", 0.0)
        if radius > 0 and depth / radius > 4.0:
            findings.append(
                DFMFinding(
                    finding_id=f"DFM-ACC-{cid}",
                    component_id=cid,
                    category="FEATURE_ACCESSIBILITY",
                    severity="MAJOR",
                    description=f"Cavity depth-to-radius ratio ({depth:.1f}mm / {radius:.1f}mm = {depth/radius:.1f}) exceeds 4:1.",
                    rationale="Requires extended reach end-mill leading to excessive tool deflection, chatter, and poor surface finish.",
                    evidence_level="E3",
                    evidence_ref="DIN ISO 2768 / Standard Machining Design Handbook",
                )
            )

        # Rule 2: Minimum wall thickness
        wall = component.get("wall_thickness_mm")
        if wall is not None:
            if "SHEET_METAL" in proc and wall < 0.6:
                findings.append(
                    DFMFinding(
                        finding_id=f"DFM-WALL-{cid}",
                        component_id=cid,
                        category="WALL_THICKNESS",
                        severity="CRITICAL",
                        description=f"Sheet metal wall thickness {wall}mm is below standard handling and punching threshold (0.6mm).",
                        rationale="Thin sheet metal risks tearing and severe wrinkling during brake forming.",
                        evidence_level="E3",
                    )
                )
            elif "INJECTION_MOLDING" in proc and wall < 0.8:
                findings.append(
                    DFMFinding(
                        finding_id=f"DFM-WALL-{cid}",
                        component_id=cid,
                        category="WALL_THICKNESS",
                        severity="CRITICAL",
                        description=f"Injection molded wall thickness {wall}mm risks short shots and high injection pressure.",
                        rationale="Thermoplastic flow front cools prematurely in thin cross sections.",
                        evidence_level="E3",
                    )
                )

        # Rule 3: Draft angle for molded/cast parts
        draft = component.get("draft_angle_deg")
        if draft is not None and ("INJECTION_MOLDING" in proc or "CASTING" in proc):
            if draft < 1.0:
                findings.append(
                    DFMFinding(
                        finding_id=f"DFM-DRAFT-{cid}",
                        component_id=cid,
                        category="DRAFT_ANGLE",
                        severity="BLOCKER",
                        description=f"Draft angle of {draft} deg is insufficient for mold release.",
                        rationale="Minimum 1.0 to 1.5 degrees draft required to prevent part scuffing and ejector pin punch-through.",
                        evidence_level="E3",
                    )
                )

        # Rule 4: Material / Process Incompatibility
        if ("CAST_IRON" in mat or "GRAY_IRON" in mat) and ("SHEET_METAL" in proc or "STAMPING" in proc):
            findings.append(
                DFMFinding(
                    finding_id=f"DFM-MISMATCH-{cid}",
                    component_id=cid,
                    category="MATERIAL_PROCESS_MISMATCH",
                    severity="BLOCKER",
                    description=f"Material {mat} has zero plastic elongation and cannot be formed by {proc}.",
                    rationale="Brittle cast irons fracture immediately upon tensile deformation in bending.",
                    evidence_level="E4",
                )
            )

        return findings
