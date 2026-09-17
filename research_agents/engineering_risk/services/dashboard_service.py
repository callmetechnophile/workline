"""
Risk Dashboard Aggregation and Metrics Service (Agent #21).
"""

from typing import List
from research_agents.engineering_risk.schemas import (
    FMEARecord,
    RiskDashboardData,
    RiskMitigation,
    RiskObject,
)


class DashboardService:
    """Aggregates metrics and health indicators for the project risk dashboard."""

    def aggregate(
        self,
        project_id: str,
        risks: List[RiskObject],
        fmea_records: List[FMEARecord],
        mitigations: List[RiskMitigation],
    ) -> RiskDashboardData:
        total = len(risks)
        open_r = sum(1 for r in risks if r.status in ("IDENTIFIED", "ASSESSED", "OPEN"))
        critical_r = sum(1 for r in risks if r.risk_level == "CRITICAL" or r.critical_review_required)
        high_r = sum(1 for r in risks if r.risk_level == "HIGH" and not r.critical_review_required)
        med_r = sum(1 for r in risks if r.risk_level == "MEDIUM")
        low_r = sum(1 for r in risks if r.risk_level == "LOW")
        mit_r = sum(1 for r in risks if r.status == "MITIGATING")
        acc_r = sum(1 for r in risks if r.status == "ACCEPTED")
        closed_r = sum(1 for r in risks if r.status == "CLOSED")
        inval_r = sum(1 for r in risks if r.status == "INVALIDATED")
        reopen_r = sum(1 for r in risks if r.status == "REOPENED")
        unverified_m = sum(1 for m in mitigations if m.status != "VERIFIED")
        spfs = sum(1 for r in risks if r.is_single_point_failure)

        rpns = [f.risk_priority_number for f in fmea_records if f.risk_priority_number is not None]
        avg_rpn = round(sum(rpns) / len(rpns), 2) if rpns else 0.0

        high_risk_comps = list({r.category for r in risks if r.risk_level in ("HIGH", "CRITICAL")})

        return RiskDashboardData(
            project_id=project_id,
            total_risks=total,
            open_risks=open_r,
            critical_risks=critical_r,
            high_risks=high_r,
            medium_risks=med_r,
            low_risks=low_r,
            mitigating_risks=mit_r,
            accepted_risks=acc_r,
            closed_risks=closed_r,
            invalidated_risks=inval_r,
            reopened_risks=reopen_r,
            unverified_mitigations=unverified_m,
            single_point_failures=spfs,
            average_rpn=avg_rpn,
            high_risk_components=high_risk_comps,
            risk_burndown_status="INSUFFICIENT_HISTORY",
        )
