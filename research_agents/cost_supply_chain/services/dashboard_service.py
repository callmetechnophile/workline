"""
Cost posture summary and metrics dashboard service.
"""

from typing import List, Optional
from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    CostDashboardData,
    LifecycleStatus,
    SupplyRisk,
)


class DashboardService:
    """Aggregates cost posture, unpriced metrics, and risk counts into dashboard payload."""

    def compile_dashboard(
        self,
        project_id: str,
        rollup: Optional[BOMCostRollup],
        risks: List[SupplyRisk],
    ) -> CostDashboardData:
        single_source = len([r for r in risks if r.risk_type.value == "SINGLE_SOURCE"])
        obsolete = len([
            r for r in risks
            if r.lifecycle_status in [LifecycleStatus.EOL, LifecycleStatus.NRND, LifecycleStatus.OBSOLETE]
        ])

        total_cost = rollup.total_unit_cost if rollup else None
        curr = rollup.currency if rollup else "USD"
        unpriced = rollup.unpriced_parts_count if rollup else 0
        target_vol = rollup.target_volume if rollup else 1000
        drivers = rollup.top_cost_drivers if rollup else []

        high_risks = [r for r in risks if r.severity.value in ["HIGH", "CRITICAL"]]

        return CostDashboardData(
            project_id=project_id,
            total_bom_cost=total_cost,
            currency=curr,
            target_volume=target_vol,
            unpriced_parts_count=unpriced,
            total_risks_count=len(risks),
            single_source_count=single_source,
            obsolete_or_nrnd_count=obsolete,
            top_drivers=drivers,
            high_risks=high_risks,
        )
