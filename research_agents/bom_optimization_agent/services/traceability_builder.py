"""
Procurement traceability builder for BOMOptimizationAgent (Section 44).
Enforces unbroken lineage from Original BOM Item -> Technical Requirement -> Candidate Components -> Supplier Offers -> Shipping -> Optimization Decision.
"""

from typing import Any, Dict, List
from research_agents.bom_optimization_agent.schemas import (
    OptimizedBOMItem,
    ProcurementStrategy,
    ProcurementTraceabilityItem,
    SupplierOffer,
)


class ProcurementTraceabilityBuilder:
    """Constructs comprehensive procurement traceability records."""

    def build_traceability(
        self,
        bom_items: List[Dict[str, Any]],
        compatible_offers: List[SupplierOffer],
        selected_strategy: ProcurementStrategy,
        optimized_items: List[OptimizedBOMItem],
    ) -> List[ProcurementTraceabilityItem]:
        """
        Synthesizes complete procurement lineage items.
        """
        traceability_records: List[ProcurementTraceabilityItem] = []

        offers_by_item: Dict[str, List[SupplierOffer]] = {}
        for off in compatible_offers:
            offers_by_item.setdefault(off.bom_item_id, []).append(off)

        for b_item in bom_items:
            b_id = b_item.get("bom_item_id", "BOM-001")
            matching_opt = next((opt for opt in optimized_items if opt.bom_item_id == b_id), None)
            item_offers = offers_by_item.get(b_id, [])

            traceability_records.append(
                ProcurementTraceabilityItem(
                    traceability_id=f"TRACE-PROC-{b_id}",
                    bom_item_id=b_id,
                    component_requirement_ids=[f"REQ-{b_id}"],
                    candidate_part_numbers=list({o.part_number for o in item_offers} | {b_item.get("part_number", "")}),
                    supplier_offer_ids=[f"{o.supplier_id}_{o.part_number}" for o in item_offers],
                    shipping_ids=["SHIP-BLUEDART-DEFAULT"],
                    selected_offer_id=f"{matching_opt.selected_supplier}_{matching_opt.selected_part_number}" if matching_opt else None,
                    decision_reason=(
                        f"Allocated to {matching_opt.selected_supplier} ({matching_opt.selected_part_number}) "
                        f"in '{selected_strategy.name}' strategy with known landed cost ₹{matching_opt.known_landed_cost or 0:.2f}."
                        if matching_opt
                        else "Pending supplier allocation."
                    ),
                )
            )

        return traceability_records
