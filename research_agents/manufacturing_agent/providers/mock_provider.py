"""
Deterministic Mock reasoning provider for Manufacturing / DFM-DFA Agent (Agent #24).
"""

from typing import Any, Dict, List
from research_agents.manufacturing_agent.providers.base import ReasoningProvider
from research_agents.manufacturing_agent.schemas import (
    DFAFinding,
    DFMFinding,
    ManufacturingRecommendation,
)


class MockManufacturingProvider(ReasoningProvider):
    """Deterministic mock provider for offline tests and evaluation benchmarks."""

    async def analyze_dfm_dfa(
        self,
        project_context: Dict[str, Any],
        components: List[Dict[str, Any]],
        assemblies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        dfm_findings: List[DFMFinding] = []
        dfa_findings: List[DFAFinding] = []

        # Analyze components for standard DFM rules
        for c in components or []:
            cid = c.get("component_id", "COMP-UNKNOWN")
            mfg_proc = c.get("intended_process", "CNC_MACHINING")
            material = c.get("material", "ALUMINUM_6061")

            # Check 1: Deep pocket / feature accessibility
            if c.get("pocket_depth_mm", 0) > 4 * c.get("pocket_corner_radius_mm", 5):
                dfm_findings.append(
                    DFMFinding(
                        finding_id=f"DFM-ACC-{cid}",
                        component_id=cid,
                        category="FEATURE_ACCESSIBILITY",
                        severity="MAJOR",
                        description=f"Deep cavity aspect ratio > 4:1 requires long-reach end mill causing tool deflection and chatter.",
                        rationale="Standard CNC machining guideline suggests cavity depth <= 3x corner radius for standard tooling.",
                        evidence_level="E3",
                        evidence_ref="Machinery's Handbook 31st Ed - CNC Milling Guidelines",
                    )
                )

            # Check 2: Unnecessarily tight tolerance
            if c.get("min_tolerance_mm", 1.0) < 0.01:
                dfm_findings.append(
                    DFMFinding(
                        finding_id=f"DFM-TOL-{cid}",
                        component_id=cid,
                        category="TOLERANCE_DIFFICULTY",
                        severity="CRITICAL",
                        description=f"Tolerance span < 0.01mm exceeds standard 3-axis CNC capability and requires jig grinding or EDM.",
                        rationale="Sub-10 micron tolerances exponentially increase cycle time and scrap rates.",
                        evidence_level="E3",
                    )
                )

            # Check 3: Material / Process Mismatch
            if "cast iron" in str(material).lower() and "sheet metal" in str(mfg_proc).lower():
                dfm_findings.append(
                    DFMFinding(
                        finding_id=f"DFM-MAT-{cid}",
                        component_id=cid,
                        category="MATERIAL_PROCESS_MISMATCH",
                        severity="BLOCKER",
                        description="Cast Iron cannot undergo sheet-metal stamping/bending due to low ductility and high brittleness.",
                        rationale="Brittle materials fracture under plastic bending deformation.",
                        evidence_level="E3",
                    )
                )

        # Analyze assemblies for DFA rules
        for a in assemblies or []:
            aid = a.get("assembly_id", "ASSY-MAIN")
            fasteners = a.get("fastener_count", 0)
            if fasteners > 12:
                dfa_findings.append(
                    DFAFinding(
                        finding_id=f"DFA-FAST-{aid}",
                        assembly_id=aid,
                        category="FASTENER_COUNT",
                        severity="MAJOR",
                        description=f"High fastener count ({fasteners} fasteners) increases manual assembly time and torque error risk.",
                        rationale="Boothroyd Dewhurst DFA guidelines recommend snap-fits or consolidated fastening.",
                        evidence_level="E3",
                    )
                )

            if a.get("has_orientation_ambiguity", False):
                dfa_findings.append(
                    DFAFinding(
                        finding_id=f"DFA-POKA-{aid}",
                        assembly_id=aid,
                        category="ORIENTATION_AMBIGUITY",
                        severity="CRITICAL",
                        description="Symmetric or near-symmetric mating interface allows 180-degree inverted assembly error.",
                        rationale="Lack of keyed features or asymmetry permits reverse installation.",
                        proposed_poka_yoke="Introduce asymmetrical mounting pin or offset bolt pattern to enforce singular insertion orientation.",
                        evidence_level="E3",
                    )
                )

        return {"dfm_findings": dfm_findings, "dfa_findings": dfa_findings}

    async def draft_recommendations(
        self,
        dfm_findings: List[DFMFinding],
        dfa_findings: List[DFAFinding],
    ) -> List[ManufacturingRecommendation]:
        recs: List[ManufacturingRecommendation] = []
        for f in dfm_findings:
            if f.category == "FEATURE_ACCESSIBILITY":
                recs.append(
                    ManufacturingRecommendation(
                        recommendation_id=f"REC-{f.finding_id}",
                        finding_id=f.finding_id,
                        component_id=f.component_id,
                        current_condition="Cavity depth exceeds 4x internal corner radius.",
                        proposed_change="Increase internal corner radii from 2mm to 4mm or split pocket into two-stage stepped pocket.",
                        engineering_rationale="Allows standard 8mm roughing end mill to reach bottom without custom extended tooling or tool deflection.",
                        expected_manufacturing_impact="Eliminates tool chatter, reduces cycle time by ~30%, and extends cutting tool life.",
                        expected_assembly_impact="No direct impact on assembly.",
                        possible_engineering_tradeoffs="Marginal reduction in internal pocket volume (~2%).",
                        confidence=0.95,
                        evidence_level="E3",
                    )
                )
            elif f.category == "TOLERANCE_DIFFICULTY":
                recs.append(
                    ManufacturingRecommendation(
                        recommendation_id=f"REC-{f.finding_id}",
                        finding_id=f.finding_id,
                        component_id=f.component_id,
                        current_condition="Linear dimensional tolerance is +/- 0.005mm.",
                        proposed_change="Relax non-critical clearance tolerance to +/- 0.025mm, or add precision locating dowel pins for alignment.",
                        engineering_rationale="Decouples structural mounting tolerance from precision alignment requirements.",
                        expected_manufacturing_impact="Allows standard CNC machining without dedicated temperature-controlled grinding.",
                        expected_assembly_impact="Improves repeatability with standardized dowel pin alignment.",
                        possible_engineering_tradeoffs="Requires adding 2 reamed dowel holes.",
                        confidence=0.92,
                        evidence_level="E3",
                    )
                )

        for d in dfa_findings:
            if d.category == "ORIENTATION_AMBIGUITY":
                recs.append(
                    ManufacturingRecommendation(
                        recommendation_id=f"REC-{d.finding_id}",
                        finding_id=d.finding_id,
                        component_id=d.affected_component_ids[0] if d.affected_component_ids else "CHASSIS",
                        current_condition="Symmetrical 4-bolt flange allows reverse assembly.",
                        proposed_change="Implement keyed alignment tab and asymmetric hole spacing (offset 1 bolt by 5mm).",
                        engineering_rationale="Physical poka-yoke guarantees correct electrical connector orientation during blind assembly.",
                        expected_manufacturing_impact="Zero cost delta during laser cutting or CNC machining.",
                        expected_assembly_impact="Eliminates 100% of reverse installation defects on assembly line.",
                        possible_engineering_tradeoffs="Loss of rotational symmetry for universal mounting.",
                        confidence=0.98,
                        evidence_level="E3",
                    )
                )

        return recs
