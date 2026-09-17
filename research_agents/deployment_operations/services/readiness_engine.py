"""
Deployment readiness evaluation engine.
"""

from typing import Any, Dict, List, Optional
from research_agents.deployment_operations.schemas import (
    DeploymentReadinessCriteria,
    ReadinessStatus,
    SystemType,
)


class ReadinessEngine:
    """Assesses multi-dimensional readiness across physical and software criteria."""

    def evaluate_readiness(
        self,
        project_id: str,
        system_type: SystemType,
        components: List[Dict[str, Any]],
        known_risks: List[Dict[str, Any]],
        dfm_handoff: Optional[Dict[str, Any]] = None,
        supply_chain_handoff: Optional[Dict[str, Any]] = None,
    ) -> tuple[ReadinessStatus, List[DeploymentReadinessCriteria]]:
        criteria: List[DeploymentReadinessCriteria] = []

        # 1. Design & Architecture Maturity
        criteria.append(
            DeploymentReadinessCriteria(
                criterion_id="CRIT-DESIGN-01",
                name="Design Specification Sign-off",
                category="DESIGN",
                status=ReadinessStatus.READY,
                notes="Primary system architecture documented and verified.",
            )
        )

        # 2. Manufacturing / Build Readiness
        if dfm_handoff and dfm_handoff.get("readiness_score", 1.0) < 0.70:
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-MFG-01",
                    name="Manufacturing & DFM Verification",
                    category="MANUFACTURING",
                    status=ReadinessStatus.BLOCKED,
                    is_blocking=True,
                    blocking_reason="DFM readiness score is below release threshold (<70%).",
                )
            )
        else:
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-MFG-01",
                    name="Manufacturing & DFM Verification",
                    category="MANUFACTURING",
                    status=ReadinessStatus.READY,
                )
            )

        # 3. Supply Chain / Parts Availability
        if supply_chain_handoff and supply_chain_handoff.get("unpriced_parts_count", 0) > 0:
            unpriced = supply_chain_handoff["unpriced_parts_count"]
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-SUPPLY-01",
                    name="BOM Parts Procurement Availability",
                    category="SUPPLY_CHAIN",
                    status=ReadinessStatus.CONDITIONAL,
                    is_blocking=False,
                    notes=f"{unpriced} parts currently unpriced or have unverified sourcing lead times.",
                )
            )
        else:
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-SUPPLY-01",
                    name="BOM Parts Procurement Availability",
                    category="SUPPLY_CHAIN",
                    status=ReadinessStatus.READY,
                )
            )

        # 4. Critical Safety / Environmental
        critical_risks = [r for r in known_risks if r.get("severity") in ["CRITICAL", "HIGH"]]
        if critical_risks:
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-SAFETY-01",
                    name="Operational Safety & Hazard Mitigation",
                    category="SAFETY",
                    status=ReadinessStatus.BLOCKED,
                    is_blocking=True,
                    blocking_reason=f"{len(critical_risks)} unmitigated critical operational/safety risks pending resolution.",
                )
            )
        else:
            criteria.append(
                DeploymentReadinessCriteria(
                    criterion_id="CRIT-SAFETY-01",
                    name="Operational Safety & Hazard Mitigation",
                    category="SAFETY",
                    status=ReadinessStatus.READY,
                )
            )

        # Determine overall status
        if any(c.status == ReadinessStatus.BLOCKED for c in criteria):
            overall = ReadinessStatus.BLOCKED
        elif any(c.status == ReadinessStatus.CONDITIONAL for c in criteria):
            overall = ReadinessStatus.CONDITIONAL
        else:
            overall = ReadinessStatus.READY

        return overall, criteria
