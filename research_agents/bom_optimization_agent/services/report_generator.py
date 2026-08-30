"""
Publication-ready Markdown Procurement Optimization report generator for BOMOptimizationAgent (Section 45).
"""

from typing import Any, Dict, List
from research_agents.bom_optimization_agent.schemas import (
    CostSummary,
    Location,
    OptimizedBOMItem,
    ProcurementStrategy,
    ProcurementTraceabilityItem,
    ProjectMeta,
    SupplierOrder,
)


class ProcurementReportGenerator:
    """Renders comprehensive 17-section Markdown Procurement Optimization Report."""

    def generate_report(
        self,
        project: ProjectMeta,
        bom_id: str,
        optimization_id: str,
        destination: Location,
        selected_strategy: ProcurementStrategy,
        all_strategies: List[ProcurementStrategy],
        optimized_items: List[OptimizedBOMItem],
        orders: List[SupplierOrder],
        alternatives: List[Dict[str, Any]],
        compat_warnings: List[str],
        proc_warnings: List[str],
        cost_summary: CostSummary,
        traceability: List[ProcurementTraceabilityItem],
        assumptions: List[Dict[str, Any]],
        unknowns: List[Dict[str, Any]],
    ) -> str:
        """Assembles all 17 sections into Markdown."""
        lines: List[str] = []

        # Title
        lines.append(f"# Procurement Optimization Report: {project.title}\n")
        lines.append(f"**Optimization ID:** `{optimization_id}` | **BOM ID:** `{bom_id}`  ")
        lines.append(f"**Recommended Strategy:** `{selected_strategy.name}`  ")
        lines.append(f"**Total Known Landed Cost:** **₹{cost_summary.total_known_landed_cost:,.2f}** ({cost_summary.supplier_count} Suppliers, {cost_summary.order_count} Orders)\n")

        # 1. Project
        lines.append("## 1. Project\n")
        lines.append(f"- **Title:** {project.title}")
        if project.project_id:
            lines.append(f"- **Project ID:** `{project.project_id}`")
        if project.constraints.maximum_budget:
            lines.append(f"- **Budget Constraint:** ₹{project.constraints.maximum_budget:,.2f}")
        if project.constraints.maximum_delivery_days:
            lines.append(f"- **Max Delivery Constraint:** {project.constraints.maximum_delivery_days} days")
        lines.append("")

        # 2. BOM Summary
        lines.append("## 2. BOM Summary\n")
        lines.append(f"- **Total Optimized Line Items:** `{len(optimized_items)}`")
        lines.append(f"- **Consolidated Supplier Orders:** `{len(orders)}`")
        lines.append(f"- **Total Product Subtotal:** ₹{cost_summary.total_product_cost:,.2f}")
        lines.append(f"- **Total Freight / Logistics:** ₹{cost_summary.total_shipping_cost:,.2f}")
        lines.append(f"- **Total Landed Cost:** **₹{cost_summary.total_known_landed_cost:,.2f}**")
        lines.append("")

        # 3. Optimization Objective
        lines.append("## 3. Optimization Objective\n")
        lines.append("Minimize total known landed cost while strictly preserving engineering compatibility, respecting distributor MOQs, and consolidating supplier shipments.\n")

        # 4. Destination
        lines.append("## 4. Destination\n")
        lines.append(f"**Delivery Target:** {destination.city}, {destination.state}, {destination.country} (PIN: `{destination.postal_code or 'N/A'}`)\n")

        # 5. Recommended Procurement Strategy
        lines.append("## 5. Recommended Procurement Strategy\n")
        lines.append(f"**Strategy Name:** {selected_strategy.name} (`{selected_strategy.strategy_id}`)\n")
        lines.append(f"- **Objective:** `{selected_strategy.objective}`")
        lines.append(f"- **Estimated Delivery Time:** `{selected_strategy.estimated_delivery_days or 'N/A'}` days")
        lines.append(f"- **Constraints Satisfied:** `{'YES' if selected_strategy.constraints_satisfied else 'NO'}`")
        lines.append("")

        # 6. Optimized BOM Table
        lines.append("## 6. Optimized BOM\n")
        lines.append("| Item | Part Number | Supplier | Qty | Unit Price | Product Cost | Shipping | Known Landed Cost |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for it in optimized_items:
            ship_str = f"₹{it.shipping_cost_allocated:,.2f}" if it.shipping_cost_allocated is not None else "Allocated"
            unit_str = f"₹{it.unit_price:,.2f}" if it.unit_price is not None else "Pending"
            prod_str = f"₹{it.product_cost:,.2f}" if it.product_cost is not None else "Pending"
            land_str = f"₹{it.known_landed_cost:,.2f}" if it.known_landed_cost is not None else "Pending"
            lines.append(f"| `{it.bom_item_id}` | `{it.selected_part_number}` | {it.selected_supplier} | {it.purchased_quantity} | {unit_str} | {prod_str} | {ship_str} | **{land_str}** |")
        lines.append("")

        # 7. Alternative Procurement Strategies
        lines.append("## 7. Alternative Procurement Strategies\n")
        lines.append("| Strategy Name | Objective | Product Cost | Shipping | Landed Cost | Suppliers | Est. Days | Feasible |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for s in all_strategies:
            lines.append(f"| **{s.name}** | `{s.objective}` | ₹{s.total_product_cost:,.2f} | ₹{s.total_shipping_cost:,.2f} | **₹{s.total_known_landed_cost:,.2f}** | {s.supplier_count} | {s.estimated_delivery_days or 'TBD'}d | {'✓' if s.constraints_satisfied else '✗'} |")
        lines.append("")

        # 8. Alternative Components
        lines.append("## 8. Alternative Components Evaluated\n")
        if alternatives:
            lines.append("| Part Number | Manufacturer | Compatibility | Approval Required | Rationale |")
            lines.append("|---|---|---|---|---|")
            for alt in alternatives:
                req_app = "YES" if alt.get("requires_engineering_approval") else "NO (Drop-in)"
                lines.append(f"| `{alt.get('part_number')}` | {alt.get('manufacturer')} | `{alt.get('compatibility')}` | `{req_app}` | {alt.get('reason')} |")
        else:
            lines.append("- No secondary candidate parts evaluated.")
        lines.append("")

        # 9. Supplier Consolidation
        lines.append("## 9. Supplier Order Consolidation\n")
        for o in orders:
            lines.append(f"### Order: `{o.order_id}` — {o.supplier_name} ({o.supplier_location.city}, {o.supplier_location.state})\n")
            lines.append(f"- **Items in Order:** {len(o.items)} components")
            lines.append(f"- **Product Subtotal:** ₹{o.product_subtotal:,.2f}")
            lines.append(f"- **Consolidated Shipping:** ₹{o.shipping_cost:,.2f} via `{o.carrier} ({o.shipping_mode.title()})`")
            lines.append(f"- **Order Total:** **₹{o.known_landed_cost:,.2f}** (Delivery: ~{o.delivery_estimate_days} days)")
            lines.append("")

        # 10. Shipping Analysis
        lines.append("## 10. Shipping & Freight Analysis\n")
        lines.append("Logistics costs computed using Blue Dart Express / Surface domestic freight models based on supplier origin and destination distance.\n")

        # 11. Delivery Analysis
        lines.append("## 11. Delivery Timeframe Analysis\n")
        lines.append(f"- **Fastest Available Delivery:** `{min((s.estimated_delivery_days or 99) for s in all_strategies)}` business days")
        lines.append(f"- **Selected Strategy Timeline:** `{selected_strategy.estimated_delivery_days or 'N/A'}` business days\n")

        # 12. Compatibility Warnings
        lines.append("## 12. Compatibility Warnings\n")
        if compat_warnings:
            for w in compat_warnings:
                lines.append(f"- {w}")
        else:
            lines.append("- All selected procurement candidates are 100% compliant with engineering architecture.")
        lines.append("")

        # 13. Procurement Warnings
        lines.append("## 13. Procurement Warnings\n")
        if proc_warnings or selected_strategy.warnings:
            for w in set(proc_warnings + selected_strategy.warnings):
                lines.append(f"- {w}")
        else:
            lines.append("- No active stock, lead-time, or MOQ warnings.")
        lines.append("")

        # 14. Budget Analysis
        lines.append("## 14. Budget Analysis\n")
        if project.constraints.maximum_budget:
            variance = project.constraints.maximum_budget - cost_summary.total_known_landed_cost
            if variance >= 0:
                lines.append(f"✓ Within allocated budget. Remaining budget cushion: **₹{variance:,.2f}**\n")
            else:
                lines.append(f"✗ Budget exceeded by **₹{-variance:,.2f}**.\n")
        else:
            lines.append("- No explicit project ceiling budget configured.\n")

        # 15. Unknown Costs
        lines.append("## 15. Unknown Costs\n")
        if cost_summary.unknown_costs:
            for uc in cost_summary.unknown_costs:
                lines.append(f"- {uc}")
        else:
            lines.append("- No unquantified landed charges detected.")
        lines.append("")

        # 16. Assumptions
        lines.append("## 16. Procurement Assumptions\n")
        if assumptions:
            for a in assumptions:
                lines.append(f"- {a.get('description', str(a))}")
        else:
            lines.append("- Standard GST / customs duties included in distributor base catalog quotes.")
        lines.append("")

        # 17. Traceability
        lines.append("## 17. Procurement Traceability Lineage\n")
        lines.append("| Traceability ID | BOM Item | Candidate Parts | Supplier Offers | Selected Offer | Decision Rationale |")
        lines.append("|---|---|---|---|---|---|")
        for tr in traceability:
            cand_str = ", ".join(tr.candidate_part_numbers[:2])
            offer_str = ", ".join(tr.supplier_offer_ids[:2])
            lines.append(f"| `{tr.traceability_id}` | `{tr.bom_item_id}` | `{cand_str}` | `{offer_str}` | `{tr.selected_offer_id or 'N/A'}` | {tr.decision_reason} |")
        lines.append("")

        return "\n".join(lines).strip()
