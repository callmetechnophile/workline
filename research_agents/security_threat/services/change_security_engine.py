"""
Change Security Impact & Regression Detection Engine (Agent #22 -> Agent #16).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.security_threat.schemas import (
    AttackPath,
    AttackSurfaceEntry,
    ChangeSecurityImpact,
    SecurityControl,
    ThreatObject,
)


class ChangeSecurityEngine:
    """Evaluates security impact of engineering changes and flags security regressions."""

    def evaluate_change_security_impact(
        self,
        change_request: Dict[str, Any],
        active_threats: List[ThreatObject],
        active_controls: List[SecurityControl],
    ) -> ChangeSecurityImpact:
        change_id = change_request.get("change_id", "CHG-SEC-001")
        project_id = change_request.get("project_id", "PROJECT-001")
        target_artifact = change_request.get("target_artifact", "API")
        change_type = change_request.get("change_type", "ARCHITECTURE_CHANGE")

        affected_threat_ids = [t.threat_id for t in active_threats]
        affected_control_ids = []
        required_verifications = []

        is_regression = False
        reg_details = []

        # Check for weakened controls or exposed endpoints
        desc = change_request.get("description", "").lower()
        if "disable auth" in desc or "remove middleware" in desc or "public endpoint" in desc:
            is_regression = True
            reg_details.append(f"Change {change_id} disables authorization/authentication middleware on {target_artifact}")

        for ctrl in active_controls:
            if ctrl.category in ("AUTHENTICATION", "AUTHORIZATION"):
                affected_control_ids.append(ctrl.control_id)
                required_verifications.append(ctrl.control_id)

        new_surfaces = []
        if "api" in target_artifact.lower() or "new external" in desc:
            new_surfaces.append(
                AttackSurfaceEntry(
                    entry_id=f"ENTRY-NEW-{change_id}",
                    type="API",
                    exposure="PUBLIC",
                    endpoint_path=f"/api/v2/{target_artifact.lower()}",
                    authentication="JWT Bearer Token",
                    authorization="ArmorIQ Scope",
                    description=f"New public API surface introduced by change {change_id}",
                )
            )

        summary = (
            f"Change {change_id} ({change_type}) impacts {len(affected_threat_ids)} threats and {len(affected_control_ids)} controls. "
            f"Regression Detected: {is_regression}."
        )

        return ChangeSecurityImpact(
            change_id=change_id,
            project_id=project_id,
            affected_threat_ids=affected_threat_ids,
            affected_control_ids=affected_control_ids,
            new_attack_surfaces=new_surfaces,
            new_attack_paths=[],
            required_verification_ids=required_verifications,
            is_regression=is_regression,
            regression_details=reg_details,
            summary=summary,
        )
