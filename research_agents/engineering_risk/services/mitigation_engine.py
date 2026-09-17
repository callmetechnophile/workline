"""
Mitigation Lifecycle, Residual Risk Evaluation, and Verification Tracking (Agent #21).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_risk.schemas import (
    FMEARecord,
    RiskMitigation,
    RiskObject,
)


class MitigationEngine:
    """
    Manages mitigation creation, residual risk calculation, and verification updates from Agent #18.
    INVARIANTS:
    - Mitigation is created as PROPOSED, never auto-VERIFIED without Agent #18 test evidence.
    - Residual severity changes ONLY if consequence itself changes; otherwise occurrence or detection changes.
    """

    def calculate_residual_risk(
        self,
        fmea: FMEARecord,
        mitigations: List[RiskMitigation],
    ) -> FMEARecord:
        """Compute residual severity, occurrence, detection, and RPN after mitigations."""
        curr_s = fmea.severity or 5
        curr_o = fmea.occurrence or 5
        curr_d = fmea.detection or 5

        delta_s, delta_o, delta_d = 0, 0, 0
        for m in mitigations:
            # Factor in target reductions from mitigations
            red = m.target_reduction or {}
            # Preventive mitigations reduce occurrence
            if m.type == "PREVENTIVE":
                delta_o += red.get("occurrence", 2)
            # Detective mitigations improve detection (lower detection score)
            elif m.type == "DETECTIVE":
                delta_d += red.get("detection", 2)
            # Compensating / corrective mitigations reduce consequence/severity
            elif m.type in ("COMPENSATING", "CORRECTIVE"):
                delta_s += red.get("severity", 1)

        # Invariant: minimum scale is 1
        res_s = max(1, curr_s - delta_s)
        res_o = max(1, curr_o - delta_o)
        res_d = max(1, curr_d - delta_d)
        res_rpn = res_s * res_o * res_d

        fmea.residual_severity = res_s
        fmea.residual_occurrence = res_o
        fmea.residual_detection = res_d
        fmea.residual_rpn = res_rpn

        logger.debug(
            f"FMEA {fmea.fmea_id} Residual RPN: {fmea.risk_priority_number} -> {res_rpn} (S:{curr_s}->{res_s}, O:{curr_o}->{res_o}, D:{curr_d}->{res_d})"
        )
        return fmea

    def verify_mitigation(
        self,
        mitigation: RiskMitigation,
        verification_evidence: Dict[str, Any],
    ) -> RiskMitigation:
        """Update mitigation status to VERIFIED when Agent #18 supplies passing evidence."""
        verdict = verification_evidence.get("verdict") or verification_evidence.get("status")
        if verdict in ("PASS", "VERIFIED"):
            mitigation.status = "VERIFIED"
            mitigation.verification_id = verification_evidence.get("verification_id", f"VER-{mitigation.mitigation_id}")
            mitigation.verification_evidence_ref = verification_evidence.get("evidence_ref", "Agent #18 Test Evidence Report")
            mitigation.updated_at = datetime.now(timezone.utc).isoformat()
            logger.info(f"Mitigation {mitigation.mitigation_id} marked VERIFIED by Agent #18.")
        else:
            logger.warning(
                f"Mitigation {mitigation.mitigation_id} verification evidence invalid or failing: {verdict}"
            )
        return mitigation
