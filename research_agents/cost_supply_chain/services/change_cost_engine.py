"""
Engineering Change Order (ECO/ECR) cost impact analysis engine.
Integrates with Agent #16 (EngineeringChangeControlAgent).
"""

from research_agents.cost_supply_chain.schemas import ChangeCostImpact


class ChangeCostEngine:
    """Assesses financial impact of proposed engineering design or sourcing changes."""

    def evaluate_change_cost(
        self,
        change_id: str,
        project_id: str,
        title: str,
        recurring_unit_delta: float,
        tooling_nre_delta: float,
        scrap_or_rework_cost: float = 0.0,
        annualized_volume: int = 1000,
    ) -> ChangeCostImpact:
        annual_impact = (recurring_unit_delta * annualized_volume) + tooling_nre_delta + scrap_or_rework_cost
        annual_impact = round(annual_impact, 2)

        if annual_impact <= 0:
            recommendation = "APPROVE"
            rationale = (
                f"Change yields annual net savings of ${abs(annual_impact):.2f} "
                f"at {annualized_volume} annual production volume."
            )
        elif recurring_unit_delta < 0 and annual_impact > 0:
            payback_years = round((tooling_nre_delta + scrap_or_rework_cost) / (abs(recurring_unit_delta) * annualized_volume), 1)
            recommendation = "APPROVE_CONDITIONAL" if payback_years < 2.0 else "REVIEW_REQUIRED"
            rationale = (
                f"Change reduces unit cost by ${abs(recurring_unit_delta):.2f}, "
                f"paying back ${tooling_nre_delta + scrap_or_rework_cost:.2f} initial tooling/scrap investment in {payback_years} years."
            )
        else:
            recommendation = "REVIEW_REQUIRED"
            rationale = (
                f"Change introduces net cost increase of ${annual_impact:.2f} annually. "
                f"Verify justification (e.g. mandatory safety, compliance, or reliability improvement)."
            )

        return ChangeCostImpact(
            change_id=change_id,
            project_id=project_id,
            title=title,
            recurring_unit_delta=round(recurring_unit_delta, 4),
            tooling_nre_delta=round(tooling_nre_delta, 2),
            scrap_or_rework_cost=round(scrap_or_rework_cost, 2),
            annualized_volume=annualized_volume,
            annual_cost_impact=annual_impact,
            recommendation=recommendation,
            rationale=rationale,
        )
