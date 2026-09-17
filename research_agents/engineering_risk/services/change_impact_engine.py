"""
Change Impact Analysis and Risk Invalidation Engine (Agent #21 -> Agent #16).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_risk.schemas import (
    ChangeRiskImpact,
    FailureMode,
    FMEARecord,
    RiskMitigation,
    RiskObject,
    RiskReassessmentPlan,
)


class ChangeImpactEngine:
    """
    Evaluates impact of engineering changes (from Agent #16) on active risks, failure modes, and mitigations.
    """

    def evaluate_change_impact(
        self,
        change_request: Dict[str, Any],
        active_risks: List[RiskObject],
        failure_modes: List[FailureMode],
        fmea_records: List[FMEARecord],
        mitigations: List[RiskMitigation],
    ) -> ChangeRiskImpact:
        change_id = change_request.get("change_id", "CHG-001")
        project_id = change_request.get("project_id", "proj_01")
        target_artifact = change_request.get("target_artifact", "BOM")
        change_type = change_request.get("change_type", "COMPONENT_CHANGE")

        affected_risk_ids = []
        affected_fm_ids = []
        invalidated_mit_ids = []

        # Correlate change with active risks
        for r in active_risks:
            affected_risk_ids.append(r.risk_id)
            r.status = "REOPENED" if r.status == "CLOSED" else "ASSESSED"
            r.updated_at = datetime.now(timezone.utc).isoformat()

        for fm in failure_modes:
            affected_fm_ids.append(fm.failure_mode_id)

        for mit in mitigations:
            if mit.status == "VERIFIED":
                # Invalidate previous verification because component changed
                mit.status = "IMPLEMENTED"
                invalidated_mit_ids.append(mit.mitigation_id)

        summary = f"Change {change_id} ({change_type} on {target_artifact}) impacts {len(affected_risk_ids)} risks and {len(affected_fm_ids)} failure modes. {len(invalidated_mit_ids)} mitigations require re-verification."

        return ChangeRiskImpact(
            change_id=change_id,
            project_id=project_id,
            affected_risk_ids=affected_risk_ids,
            affected_failure_mode_ids=affected_fm_ids,
            invalidated_mitigation_ids=invalidated_mit_ids,
            reassessed_fmea_records=fmea_records,
            verification_required_ids=invalidated_mit_ids,
            summary=summary,
        )

    def create_reassessment_plan(
        self,
        impact: ChangeRiskImpact,
    ) -> RiskReassessmentPlan:
        tasks = []
        for r_id in impact.affected_risk_ids:
            tasks.append({
                "task_id": f"TASK-REASSESS-{r_id}",
                "description": f"Reassess RPN and failure causes for {r_id}",
                "priority": "HIGH",
            })
        return RiskReassessmentPlan(
            change_id=impact.change_id,
            project_id=impact.project_id,
            tasks=tasks,
            required_verifications=impact.verification_required_ids,
        )
