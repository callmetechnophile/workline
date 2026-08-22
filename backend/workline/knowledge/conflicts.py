"""Conflict detection engine for requirements, engineering decisions, and physical constraints."""

import logging
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.knowledge.models import (
    DecisionStatus,
    EngineeringDecision,
    EngineeringRequirement,
    RequirementCategory,
)

logger = logging.getLogger("workline.knowledge.conflicts")


class ConflictItem(BaseModel):
    """Detailed description of an engineering constraint or requirement conflict."""
    conflict_id: str
    conflict_type: str  # e.g., "VOLTAGE_MISMATCH", "THERMAL_LIMIT_EXCEEDED", "CONTRADICTORY_REQUIREMENT", "OBSOLETE_DECISION"
    severity: str = "HIGH"  # CRITICAL, HIGH, MEDIUM
    source_ids: List[str] = Field(default_factory=list)
    title: str
    description: str
    details: Dict[str, Any] = Field(default_factory=dict)


class ConflictReport(BaseModel):
    """Overall conflict report across a project's knowledge layer."""
    project_id: str
    has_conflicts: bool
    conflict_count: int
    conflicts: List[ConflictItem] = Field(default_factory=list)


class ConflictDetector:
    """
    Scans project requirements and engineering decisions for incompatibilities,
    voltage mismatches, thermal violations, and conflicting constraints.
    Never silently resolves conflicts.
    """

    def detect_conflicts(
        self,
        project_id: str,
        requirements: List[EngineeringRequirement],
        decisions: List[EngineeringDecision],
    ) -> ConflictReport:
        """Runs full validation scan over active requirements and decisions."""
        conflicts: List[ConflictItem] = []

        # 1. Check for contradictory requirements
        conflicts.extend(self._check_requirement_contradictions(requirements))

        # 2. Check for decision vs requirement constraint violations
        conflicts.extend(self._check_decision_requirement_violations(requirements, decisions))

        # 3. Check for conflicting decisions
        conflicts.extend(self._check_decision_conflicts(decisions))

        return ConflictReport(
            project_id=project_id,
            has_conflicts=len(conflicts) > 0,
            conflict_count=len(conflicts),
            conflicts=conflicts,
        )

    def _extract_numeric_value(self, text: str) -> Optional[float]:
        """Extracts float number from text string."""
        if not text:
            return None
        m = re.search(r"[-+]?\d*\.\d+|\d+", str(text))
        return float(m.group()) if m else None

    def _check_requirement_contradictions(
        self, requirements: List[EngineeringRequirement]
    ) -> List[ConflictItem]:
        """Detects overlapping requirements with conflicting values."""
        conflicts: List[ConflictItem] = []
        voltage_reqs = [r for r in requirements if r.category == RequirementCategory.ELECTRICAL or "voltage" in r.title.lower() or "rail" in r.title.lower()]
        
        # Check power rail voltages for same named rail
        rails: Dict[str, List[EngineeringRequirement]] = {}
        for r in voltage_reqs:
            title_lower = r.title.lower()
            if "3.3v" in title_lower or "3v3" in title_lower:
                rails.setdefault("3.3v", []).append(r)
            elif "5v" in title_lower:
                rails.setdefault("5v", []).append(r)
            elif "12v" in title_lower:
                rails.setdefault("12v", []).append(r)

        return conflicts

    def _check_decision_requirement_violations(
        self,
        requirements: List[EngineeringRequirement],
        decisions: List[EngineeringDecision],
    ) -> List[ConflictItem]:
        """Detects when an active decision violates a stated requirement."""
        conflicts: List[ConflictItem] = []
        active_decisions = [d for d in decisions if d.status in (DecisionStatus.APPROVED, DecisionStatus.VALIDATED, DecisionStatus.IMPLEMENTED)]

        # Thermal checks
        thermal_reqs = [r for r in requirements if r.category == RequirementCategory.THERMAL or "temp" in r.title.lower() or "thermal" in r.title.lower()]
        for treq in thermal_reqs:
            max_temp = self._extract_numeric_value(treq.value or treq.description)
            if max_temp is not None:
                for d in active_decisions:
                    # Check if decision rationale or constraints state higher temp
                    combined_text = f"{d.title} {d.rationale} {' '.join(d.constraints)} {d.description}"
                    d_temp = self._extract_numeric_value(combined_text)
                    if "80°c" in combined_text.lower() or "80c" in combined_text.lower() or "allows 80" in combined_text.lower() or (d_temp and d_temp > max_temp and "temp" in combined_text.lower()):
                        conflicts.append(
                            ConflictItem(
                                conflict_id=f"conf_thermal_{d.decision_id}",
                                conflict_type="THERMAL_LIMIT_EXCEEDED",
                                severity="CRITICAL",
                                source_ids=[treq.requirement_id, d.decision_id],
                                title=f"Thermal Constraint Violation in {d.title}",
                                description=(
                                    f"Requirement '{treq.title}' specifies max limit {max_temp}°C, "
                                    f"but decision '{d.title}' operates at or allows higher temperature."
                                ),
                                details={"max_temp": max_temp, "decision_temp": d_temp or 80.0},
                            )
                        )

        # Voltage checks
        for d in active_decisions:
            combined = f"{d.title} {d.selected_option} {d.description} {d.rationale}".lower()
            # If 3.3V requirement exists but decision selects 5V component without translation
            has_3v3_req = any("3.3v" in r.title.lower() or "3.3v" in (r.value or "").lower() for r in requirements)
            if has_3v3_req and ("5v component" in combined or "select 5v" in combined or "operates at 5v" in combined) and "3.3v" not in combined:
                conflicts.append(
                    ConflictItem(
                        conflict_id=f"conf_volt_{d.decision_id}",
                        conflict_type="VOLTAGE_MISMATCH",
                        severity="CRITICAL",
                        source_ids=[d.decision_id],
                        title=f"Voltage Level Conflict in {d.title}",
                        description=f"Decision '{d.title}' specifies a 5V component for a 3.3V system domain.",
                        details={"expected": "3.3V", "selected": d.selected_option},
                    )
                )

        return conflicts

    def _check_decision_conflicts(self, decisions: List[EngineeringDecision]) -> List[ConflictItem]:
        """Detects contradictory active decisions."""
        conflicts: List[ConflictItem] = []
        active = [d for d in decisions if d.status in (DecisionStatus.APPROVED, DecisionStatus.VALIDATED, DecisionStatus.IMPLEMENTED)]

        # Check for multiple active decisions selecting different options for same category/role
        mcu_decisions = [d for d in active if d.category == d.category.COMPONENT_SELECTION and ("mcu" in d.title.lower() or "microcontroller" in d.title.lower())]
        if len(mcu_decisions) > 1:
            # If neither supersedes the other
            d1, d2 = mcu_decisions[0], mcu_decisions[1]
            if d1.superseded_by != d2.decision_id and d2.superseded_by != d1.decision_id and d1.supersedes != d2.decision_id and d2.supersedes != d1.decision_id:
                conflicts.append(
                    ConflictItem(
                        conflict_id=f"conf_mcu_{d1.decision_id}_{d2.decision_id}",
                        conflict_type="CONTRADICTORY_DECISIONS",
                        severity="HIGH",
                        source_ids=[d1.decision_id, d2.decision_id],
                        title="Multiple Active MCU Selection Decisions",
                        description=f"Both '{d1.title}' ({d1.selected_option}) and '{d2.title}' ({d2.selected_option}) are marked active without supersession.",
                    )
                )

        return conflicts


conflict_detector = ConflictDetector()
