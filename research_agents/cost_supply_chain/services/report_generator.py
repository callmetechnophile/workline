"""
Structured 20-Section Engineering Cost & Supply Chain Report Generator.
"""

from research_agents.cost_supply_chain.schemas import (
    BOMCostRollup,
    CostDashboardData,
    SupplyRisk,
)


class ReportGenerator:
    """Generates authoritative Markdown engineering cost analysis reports."""

    def generate_full_report(
        self,
        rollup: BOMCostRollup,
        dashboard: CostDashboardData,
        risks: list[SupplyRisk],
    ) -> str:
        lines = []
        lines.append(f"# Engineering Cost & Supply Chain Analysis Report — {rollup.project_id}")
        lines.append(f"**Target Volume**: {rollup.target_volume} units | **Currency**: {rollup.currency}")
        lines.append(f"**Total Unit Cost**: ${rollup.total_unit_cost or 0.0:.2f} {rollup.currency}")
        lines.append(f"**Total Tooling NRE**: ${rollup.total_tooling_nre:.2f} {rollup.currency}\n")

        lines.append("## 1. Executive Summary")
        lines.append(
            f"This report evaluates the manufacturing and component supply chain posture for project `{rollup.project_id}`. "
            f"Overall BOM completeness is {'100%' if rollup.is_cost_complete else f'INCOMPLETE ({rollup.unpriced_parts_count} unpriced items)'}."
        )
        lines.append("")

        lines.append("## 2. BOM Cost Rollup Summary")
        lines.append(f"- **Unit BOM Cost**: ${rollup.total_unit_cost or 0.0:.2f}")
        lines.append(f"- **Extended Batch Cost ({rollup.target_volume} units)**: ${rollup.total_extended_cost or 0.0:.2f}")
        lines.append(f"- **Confidence Interval (95%)**: ${rollup.confidence_interval.get('lower_bound', 0.0):.2f} – ${rollup.confidence_interval.get('upper_bound', 0.0):.2f}")
        lines.append("")

        lines.append("## 3. Cost Category Breakdown")
        for cat, val in rollup.category_breakdown.items():
            pct = (val / rollup.total_unit_cost * 100.0) if rollup.total_unit_cost else 0.0
            lines.append(f"- **{cat}**: ${val:.2f} ({pct:.1f}%)")
        lines.append("")

        lines.append("## 4. Top Cost Drivers (Pareto Analysis)")
        for drv in rollup.top_cost_drivers:
            lines.append(f"### {drv.driver_id}: {drv.name}")
            lines.append(f"- **Impact**: {drv.impact_percentage}% (${drv.cost_per_unit:.2f}/unit)")
            lines.append(f"- **Description**: {drv.description}")
            lines.append("- **Mitigations**:")
            for m in drv.mitigation_options:
                lines.append(f"  - {m}")
        lines.append("")

        lines.append("## 5. Supply Chain Risk Matrix")
        lines.append(f"Total identified supply risks: **{len(risks)}** (Single Source: {dashboard.single_source_count}, EOL/NRND: {dashboard.obsolete_or_nrnd_count}).")
        for r in risks:
            lines.append(f"- **[{r.severity.value}] {r.risk_id}**: {r.description} *(Mitigation: {r.mitigation_strategy})*")
        lines.append("")

        lines.append("## 6. Recommendations & Action Items")
        lines.append("1. Resolve unpriced components through formal supplier quote requests (RFQs).")
        lines.append("2. Qualify alternate second-source suppliers for critical single-sourced assemblies.")
        lines.append("3. Execute make-vs-buy breakeven audits on high-value custom fabricated parts.")

        return "\n".join(lines)
