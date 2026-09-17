"""
Strict Engineering Lifecycle Stage Gates & Governance Invariants (Phases 9 & 10).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from fastapi import HTTPException, status


class LifecycleGateViolation(Exception):
    """Raised when an engineering lifecycle governance constraint is violated."""
    def __init__(self, gate_name: str, reason: str):
        super().__init__(f"[Gate Violation: {gate_name}] {reason}")
        self.gate_name = gate_name
        self.reason = reason


class LifecycleStageGate:
    """
    Enforces engineering safety invariants across lifecycle stages:
    1. Simulation Gate: Releases are rejected if physics/thermal simulation fails or has high error.
    2. Sourcing Gate: Orders or production commits are rejected if BOM has unapproved or EOL components.
    3. Authorization Gate: Transitions to production require explicit human reviewer signoff.
    """

    @staticmethod
    def verify_simulation_pass(simulation_results: Dict[str, Any]):
        """Reject stage advancement if simulation failed or peak thermal exceeded threshold."""
        status = simulation_results.get("status", "").upper()
        if status in ("FAILED", "ERROR"):
            raise LifecycleGateViolation(
                "SIMULATION_GATE",
                f"Simulation status is {status}. Advancement to release/production blocked.",
            )
        
        peak_temp = simulation_results.get("peak_temperature_c") or simulation_results.get("max_temp")
        if peak_temp is not None and float(peak_temp) > 105.0:
            raise LifecycleGateViolation(
                "THERMAL_SAFETY_GATE",
                f"Peak thermal prediction ({peak_temp}°C) exceeds safe operational limit (105.0°C).",
            )
        logger.info("[LifecycleStageGate] Simulation gate passed.")

    @staticmethod
    def verify_bom_approval(bom_items: List[Dict[str, Any]], human_approval_signed: bool):
        """Reject procurement or order dispatch if BOM contains unapproved or unavailable items."""
        if not human_approval_signed:
            raise LifecycleGateViolation(
                "HUMAN_GOVERNANCE_GATE",
                "BOM has not received required Human Reviewer signoff.",
            )

        for item in bom_items:
            lifecycle_status = (item.get("lifecycle_status") or item.get("status") or "").upper()
            if lifecycle_status in ("OBSOLETE", "EOL", "DISCONTINUED"):
                mpn = item.get("mpn") or item.get("part_number") or "Unknown"
                raise LifecycleGateViolation(
                    "BOM_SOURCING_GATE",
                    f"Component '{mpn}' is {lifecycle_status}. Sourcing blocked.",
                )
        logger.info("[LifecycleStageGate] BOM approval and sourcing gate passed.")
