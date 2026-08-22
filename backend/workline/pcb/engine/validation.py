"""PCB Engineering 12-Check Validation Engine."""

import math
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from backend.workline.pcb.engine.placement import PlacementEngine
from backend.workline.pcb.models.project import PCBProject


class ViolationReportItem(BaseModel):
    """Detailed structural violation record with engineering evidence and recommendation."""
    violation_id: str
    category: str                      # BOUNDARY, OVERLAP, KEEPOUT, CLEARANCE, FOOTPRINT, NETLIST, POWER, THERMAL, ROUTING, CONSTRAINTS
    severity: str                      # PASS, WARN, FAIL
    component: Optional[str] = None    # Reference designator
    net: Optional[str] = None          # Net name
    location: Optional[Dict[str, float]] = None # {"x": ..., "y": ...}
    description: str
    evidence: str
    recommendation: str


class PCBValidationReport(BaseModel):
    """Comprehensive design rule check (DRC) and physical integrity report."""
    project_id: str
    status: str                        # PASS, WARN, FAIL
    passed: bool
    summary: str
    total_violations_count: int
    error_count: int
    warning_count: int
    violations: List[ViolationReportItem] = Field(default_factory=list)


class PCBValidator:
    """
    Executes the 12 rigorous PCB design, physical, electrical, and thermal validation checks.
    """

    def __init__(self):
        self.placement_engine = PlacementEngine()

    def validate_project(self, project: PCBProject) -> PCBValidationReport:
        """Run all 12 validation checks."""
        violations: List[ViolationReportItem] = []

        board = project.board
        comps = project.components
        fps = project.footprints
        nets = project.nets
        rules = project.constraints

        # -------------------------------------------------------------
        # 1. BOARD BOUNDARY CHECK
        # -------------------------------------------------------------
        for cid, comp in comps.items():
            fp = fps.get(comp.footprint_id)
            if fp and not self.placement_engine.is_within_board(comp, fp, board):
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_bound_{uuid.uuid4().hex[:6]}",
                        category="BOUNDARY",
                        severity="FAIL",
                        component=comp.reference_designator,
                        location={"x": comp.x, "y": comp.y},
                        description=f"Component '{comp.reference_designator}' lies outside physical board outline.",
                        evidence=f"Coordinates ({comp.x}mm, {comp.y}mm) with footprint size {fp.body_width}x{fp.body_height}mm exceed board boundary {board.width}x{board.height}mm.",
                        recommendation=f"Relocate '{comp.reference_designator}' inside board area with at least 1.5mm edge margin.",
                    )
                )

        # -------------------------------------------------------------
        # 2. COMPONENT OVERLAP CHECK
        # -------------------------------------------------------------
        comp_list = list(comps.values())
        for i in range(len(comp_list)):
            for j in range(i + 1, len(comp_list)):
                ca = comp_list[i]
                cb = comp_list[j]
                fa = fps.get(ca.footprint_id)
                fb = fps.get(cb.footprint_id)
                if fa and fb:
                    overlap, dist = self.placement_engine.check_overlap(ca, fa, cb, fb)
                    if overlap:
                        violations.append(
                            ViolationReportItem(
                                violation_id=f"v_overlap_{uuid.uuid4().hex[:6]}",
                                category="OVERLAP",
                                severity="FAIL",
                                component=f"{ca.reference_designator} / {cb.reference_designator}",
                                location={"x": round((ca.x + cb.x) / 2.0, 1), "y": round((ca.y + cb.y) / 2.0, 1)},
                                description=f"Collision detected between '{ca.reference_designator}' and '{cb.reference_designator}'.",
                                evidence=f"Center distance is {dist:.2f}mm, which is smaller than required courtyard separation.",
                                recommendation="Increase spatial separation or re-orient components to eliminate land pattern collisions.",
                            )
                        )

        # -------------------------------------------------------------
        # 3. KEEPOUT VIOLATION CHECK
        # -------------------------------------------------------------
        for cid, comp in comps.items():
            for ko in board.keepouts:
                if ko.id == "KO_EDGE":
                    continue # Handled by boundary check
                if (ko.x <= comp.x <= ko.x + ko.width) and (ko.y <= comp.y <= ko.y + ko.height):
                    violations.append(
                        ViolationReportItem(
                            violation_id=f"v_ko_{uuid.uuid4().hex[:6]}",
                            category="KEEPOUT",
                            severity="FAIL",
                            component=comp.reference_designator,
                            location={"x": comp.x, "y": comp.y},
                            description=f"Component '{comp.reference_designator}' placed inside restricted keepout zone '{ko.name}'.",
                            evidence=f"Component coordinates ({comp.x}, {comp.y}) fall inside keepout bounds [{ko.x}, {ko.y}, {ko.width}x{ko.height}].",
                            recommendation=f"Move '{comp.reference_designator}' outside the designated keepout zone.",
                        )
                    )

        # -------------------------------------------------------------
        # 4. MINIMUM CLEARANCE CHECK
        # -------------------------------------------------------------
        min_clear = rules.minimum_clearance.value
        for i in range(len(comp_list)):
            for j in range(i + 1, len(comp_list)):
                ca = comp_list[i]
                cb = comp_list[j]
                fa = fps.get(ca.footprint_id)
                fb = fps.get(cb.footprint_id)
                if fa and fb:
                    dist = math.hypot(ca.x - cb.x, ca.y - cb.y)
                    body_dist = dist - ((fa.body_width + fb.body_width) / 2.0)
                    if 0 < body_dist < min_clear:
                        violations.append(
                            ViolationReportItem(
                                violation_id=f"v_clear_{uuid.uuid4().hex[:6]}",
                                category="CLEARANCE",
                                severity="WARN",
                                component=f"{ca.reference_designator} / {cb.reference_designator}",
                                location={"x": ca.x, "y": ca.y},
                                description=f"Component spacing ({body_dist:.2f}mm) is tighter than rule limit ({min_clear:.2f}mm).",
                                evidence=f"Spacing measured: {body_dist:.2f}mm. Minimum constraint: {min_clear:.2f}mm.",
                                recommendation=f"Increase clearance between {ca.reference_designator} and {cb.reference_designator} to >= {min_clear}mm.",
                            )
                        )

        # -------------------------------------------------------------
        # 5. MISSING FOOTPRINT CHECK
        # -------------------------------------------------------------
        for cid, comp in comps.items():
            if not comp.footprint_id or comp.footprint_id not in fps:
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_mfp_{uuid.uuid4().hex[:6]}",
                        category="FOOTPRINT",
                        severity="FAIL",
                        component=comp.reference_designator,
                        description=f"Component '{comp.reference_designator}' lacks an assigned package footprint.",
                        evidence=f"Footprint ID '{comp.footprint_id}' was not found in project footprint library.",
                        recommendation="Assign a valid standard footprint to this component.",
                    )
                )

        # -------------------------------------------------------------
        # 6. INVALID FOOTPRINT CHECK
        # -------------------------------------------------------------
        for fpid, fp in fps.items():
            if len(fp.pads) == 0 or fp.body_width <= 0.0 or fp.body_height <= 0.0:
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_ifp_{uuid.uuid4().hex[:6]}",
                        category="FOOTPRINT",
                        severity="FAIL",
                        description=f"Footprint '{fp.name}' is invalid.",
                        evidence=f"Footprint contains {len(fp.pads)} pads and dimensions {fp.body_width}x{fp.body_height}mm.",
                        recommendation="Define land pattern pads and valid physical package dimensions.",
                    )
                )

        # -------------------------------------------------------------
        # 7. UNCONNECTED NET CHECK
        # -------------------------------------------------------------
        for nid, net in nets.items():
            if len(net.nodes) <= 1:
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_unc_{uuid.uuid4().hex[:6]}",
                        category="NETLIST",
                        severity="WARN",
                        net=net.name,
                        description=f"Net '{net.name}' is single-ended or floating (unconnected).",
                        evidence=f"Net has {len(net.nodes)} node(s). At least 2 connections are required for electrical conduction.",
                        recommendation="Connect net to target recipient pin or remove dangling net definition.",
                    )
                )

        # -------------------------------------------------------------
        # 8. INVALID NET CHECK (Non-existent pin references)
        # -------------------------------------------------------------
        for nid, net in nets.items():
            for node in net.nodes:
                comp = comps.get(node.component_id)
                if not comp:
                    violations.append(
                        ViolationReportItem(
                            violation_id=f"v_invn_{uuid.uuid4().hex[:6]}",
                            category="NETLIST",
                            severity="FAIL",
                            net=net.name,
                            description=f"Net '{net.name}' references non-existent component '{node.component_id}'.",
                            evidence=f"Component ID '{node.component_id}' is missing from PCB project.",
                            recommendation="Update net node reference or define target component.",
                        )
                    )

        # -------------------------------------------------------------
        # 9. POWER VIOLATION CHECK
        # -------------------------------------------------------------
        for rname, rail in project.power.rails.items():
            if rail.estimated_current > rail.max_current:
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_pwr_{uuid.uuid4().hex[:6]}",
                        category="POWER",
                        severity="FAIL",
                        net=rail.name,
                        description=f"Power rail '{rail.name}' is overloaded.",
                        evidence=f"Estimated load {rail.estimated_current:.2f}A exceeds rail rating {rail.max_current:.2f}A.",
                        recommendation="Increase regulator current rating or reduce consumer power draw.",
                    )
                )

        # -------------------------------------------------------------
        # 10. THERMAL VIOLATION CHECK
        # -------------------------------------------------------------
        max_temp_rule = rules.maximum_temperature.value
        for cid, tcomp in project.thermal.components.items():
            est_temp = project.thermal.ambient_temperature + (tcomp.power_dissipation * tcomp.thermal_resistance_ja)
            if est_temp > max_temp_rule or est_temp > tcomp.max_junction_temperature:
                comp = comps.get(cid)
                ref_des = comp.reference_designator if comp else cid
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_thm_{uuid.uuid4().hex[:6]}",
                        category="THERMAL",
                        severity="WARN" if est_temp <= tcomp.max_junction_temperature else "FAIL",
                        component=ref_des,
                        location={"x": comp.x, "y": comp.y} if comp else None,
                        description=f"Component '{ref_des}' estimated junction temperature ({est_temp:.1f}°C) exceeds threshold ({max_temp_rule:.1f}°C).",
                        evidence=f"Power dissipation of {tcomp.power_dissipation}W at Rth_ja={tcomp.thermal_resistance_ja}°C/W creates estimated hotspot at {est_temp:.1f}°C.",
                        recommendation="Add copper thermal relief pour, thermal vias to internal GND plane, or heat sink.",
                    )
                )

        # -------------------------------------------------------------
        # 11. ROUTING CONSTRAINT VIOLATION CHECK
        # -------------------------------------------------------------
        for rule_id, rrule in project.routing.rules.items():
            if rrule.trace_width < rules.minimum_trace_width.value:
                violations.append(
                    ViolationReportItem(
                        violation_id=f"v_rt_{uuid.uuid4().hex[:6]}",
                        category="ROUTING",
                        severity="FAIL",
                        description=f"Routing rule '{rule_id}' specifies trace width ({rrule.trace_width}mm) below manufacturing minimum ({rules.minimum_trace_width.value}mm).",
                        evidence=f"Requested: {rrule.trace_width}mm. Manufacturing limit: {rules.minimum_trace_width.value}mm.",
                        recommendation=f"Increase trace width to >= {rules.minimum_trace_width.value}mm.",
                    )
                )

        # -------------------------------------------------------------
        # 12. MISSING REQUIRED CONSTRAINTS CHECK
        # -------------------------------------------------------------
        if not rules.minimum_clearance or rules.minimum_clearance.value <= 0.0:
            violations.append(
                ViolationReportItem(
                    violation_id=f"v_cst_{uuid.uuid4().hex[:6]}",
                    category="CONSTRAINTS",
                    severity="FAIL",
                    description="Missing critical minimum clearance design rule.",
                    evidence="minimum_clearance is unspecified or zero.",
                    recommendation="Set valid minimum clearance constraint.",
                )
            )

        # Calculate Status
        err_count = sum(1 for v in violations if v.severity == "FAIL")
        warn_count = sum(1 for v in violations if v.severity == "WARN")

        overall_status = "FAIL" if err_count > 0 else ("WARN" if warn_count > 0 else "PASS")
        passed = (overall_status == "PASS" or overall_status == "WARN")

        summary = f"PCB Validation {overall_status}: {err_count} Error(s), {warn_count} Warning(s) across 12 rule categories."

        return PCBValidationReport(
            project_id=project.project_id,
            status=overall_status,
            passed=passed,
            summary=summary,
            total_violations_count=len(violations),
            error_count=err_count,
            warning_count=warn_count,
            violations=violations,
        )
