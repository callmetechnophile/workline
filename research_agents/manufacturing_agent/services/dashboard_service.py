"""
Manufacturing Dashboard Posture Aggregator (Section 43).
"""

from typing import List
from research_agents.manufacturing_agent.schemas import (
    DFAModel,
    DFMFinding,
    ManufacturingDashboardData,
    ManufacturingReadiness,
    ManufacturingRecommendation,
)


class DashboardService:
    """Aggregates executive dashboard metrics for manufacturing posture."""

    def aggregate(
        self,
        project_id: str,
        components_count: int,
        dfm_findings: List[DFMFinding],
        dfa_models: List[DFAModel],
        recommendations: List[ManufacturingRecommendation],
        readiness: ManufacturingReadiness,
    ) -> ManufacturingDashboardData:
        dfa_findings_count = sum(len(m.findings) for m in dfa_models)

        return ManufacturingDashboardData(
            project_id=project_id,
            total_components_analyzed=components_count,
            total_dfm_findings=len(dfm_findings),
            total_dfa_findings=dfa_findings_count,
            blockers_count=len(readiness.active_blockers),
            recommendations_count=len(recommendations),
            readiness_verdict=readiness.verdict,
            dfm_score=readiness.dfm_score,
            dfa_score=readiness.dfa_score,
        )
