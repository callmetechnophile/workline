"""
Deterministic Failure Mode and Effects Analysis (FMEA) and RPN Engine (Agent #21).
"""

from typing import List, Optional, Tuple
from loguru import logger

from research_agents.engineering_risk.config import risk_config
from research_agents.engineering_risk.schemas import (
    FailureMode,
    FMEARecord,
    RiskLevelLiteral,
    RiskObject,
)


class FMEAEngine:
    """
    Deterministic FMEA calculator and evaluator.
    INVARIANTS:
    - RPN = Severity * Occurrence * Detection calculated deterministically.
    - No LLM arithmetic.
    - Severity >= 9 forces CRITICAL_REVIEW override regardless of RPN.
    - Missing occurrence data marked UNKNOWN / ESTIMATED with justification.
    """

    def calculate_rpn(
        self,
        severity: Optional[int],
        occurrence: Optional[int],
        detection: Optional[int],
    ) -> Optional[int]:
        """Deterministic calculation of Risk Priority Number (RPN = S * O * D)."""
        if severity is None or occurrence is None or detection is None:
            return None
        # Clamp bounds to 1..10
        s = max(1, min(10, severity))
        o = max(1, min(10, occurrence))
        d = max(1, min(10, detection))
        return s * o * d

    def evaluate_fmea(
        self,
        project_id: str,
        failure_mode: FailureMode,
        severity: int = 5,
        occurrence: int = 5,
        detection: int = 5,
        occurrence_nature: str = "ESTIMATED",
        occurrence_justification: Optional[str] = None,
        current_controls: Optional[List[str]] = None,
        recommended_actions: Optional[List[str]] = None,
    ) -> FMEARecord:
        """Create and evaluate a deterministic FMEA record."""
        # Sanitize ratings to 1..10
        s = max(1, min(10, severity))
        o = max(1, min(10, occurrence))
        d = max(1, min(10, detection))

        rpn = self.calculate_rpn(s, o, d)

        # Critical override check (Section 18)
        critical_override = False
        critical_reason = None
        if s >= risk_config.critical_safety_severity_threshold:
            critical_override = True
            critical_reason = f"Severity {s} >= {risk_config.critical_safety_severity_threshold} (Critical safety/compliance policy override)"

        controls = current_controls or [c.description for c in failure_mode.controls]

        return FMEARecord(
            project_id=project_id,
            failure_mode_id=failure_mode.failure_mode_id,
            severity=s,
            occurrence=o,
            detection=d,
            risk_priority_number=rpn,
            occurrence_nature="ACTUAL_DATA" if occurrence_nature == "ACTUAL_DATA" else "ESTIMATED",
            occurrence_justification=occurrence_justification or ("Engineering estimate based on component class" if occurrence_nature != "ACTUAL_DATA" else "Empirical test record"),
            current_controls=controls,
            recommended_actions=recommended_actions or [],
            critical_review_required=critical_override,
            critical_review_reason=critical_reason,
            status="OPEN",
        )

    def determine_risk_level(self, rpn: Optional[int], severity: Optional[int]) -> RiskLevelLiteral:
        """Map RPN and Severity to risk levels with critical override."""
        if severity is not None and severity >= risk_config.critical_safety_severity_threshold:
            return "CRITICAL"
        if rpn is None:
            return "MEDIUM"
        if rpn >= risk_config.risk_matrix.rpn_thresholds["CRITICAL"]:
            return "CRITICAL"
        if rpn >= risk_config.risk_matrix.rpn_thresholds["HIGH"]:
            return "HIGH"
        if rpn >= risk_config.risk_matrix.rpn_thresholds["MEDIUM"]:
            return "MEDIUM"
        return "LOW"
