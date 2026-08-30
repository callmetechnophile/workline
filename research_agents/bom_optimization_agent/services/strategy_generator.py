"""
Procurement strategy generation service for BOMOptimizationAgent (Sections 22, 23, 24, 31, 32).
Constructs deterministic procurement strategies: Lowest Landed Cost, Fastest Delivery, Balanced, and Minimum Suppliers.
"""

from typing import Any, Dict, List, Tuple
from research_agents.bom_optimization_agent.schemas import (
    Location,
    OptimizedBOMItem,
    ProcurementStrategy,
    ProjectConstraints,
    SupplierOffer,
    SupplierOrder,
)
from research_agents.bom_optimization_agent.services.order_consolidator import OrderConsolidator


class StrategyGenerator:
    """Evaluates multi-supplier configurations and generates 4 distinct procurement strategies."""

    def __init__(self, order_consolidator: OrderConsolidator = None):
        self.order_consolidator = order_consolidator or OrderConsolidator()

    async def generate_strategies(
        self,
        compatible_offers: List[SupplierOffer],
        bom_items: List[Dict[str, Any]],
        destination: Location,
        constraints: ProjectConstraints,
    ) -> Tuple[ProcurementStrategy, List[ProcurementStrategy], List[OptimizedBOMItem]]:
        """
        Generates 4 distinct procurement configurations and returns (selected_strategy, all_strategies, optimized_items).
        """
        # Map offers by bom_item_id
        offers_by_item: Dict[str, List[SupplierOffer]] = {}
        for off in compatible_offers:
            offers_by_item.setdefault(off.bom_item_id, []).append(off)

        # ---------------------------------------------------------------------
        # Strategy 1: Lowest Landed Cost (Surface / Economy + Best Unit Price)
        # ---------------------------------------------------------------------
        cheapest_selection: List[SupplierOffer] = []
        for b_item in bom_items:
            b_id = b_item.get("bom_item_id")
            avail_offers = offers_by_item.get(b_id, [])
            if avail_offers:
                # Pick lowest unit price offer
                best = min(avail_offers, key=lambda x: x.unit_price or float("inf"))
                cheapest_selection.append(best)

        orders_cheapest = await self.order_consolidator.consolidate_orders(
            cheapest_selection, bom_items, destination, shipping_mode="surface"
        )
        strat_cheapest = self._build_strategy(
            strat_id="STRAT-001",
            name="Lowest Landed Cost",
            objective="minimize_landed_cost",
            orders=orders_cheapest,
            constraints=constraints,
        )

        # ---------------------------------------------------------------------
        # Strategy 2: Fastest Delivery (Express / Air + Shortest Lead Time)
        # ---------------------------------------------------------------------
        fastest_selection: List[SupplierOffer] = []
        for b_item in bom_items:
            b_id = b_item.get("bom_item_id")
            avail_offers = offers_by_item.get(b_id, [])
            if avail_offers:
                # Pick shortest lead time offer
                best = min(avail_offers, key=lambda x: x.lead_time_days or 99)
                fastest_selection.append(best)

        orders_fastest = await self.order_consolidator.consolidate_orders(
            fastest_selection, bom_items, destination, shipping_mode="express"
        )
        strat_fastest = self._build_strategy(
            strat_id="STRAT-002",
            name="Fastest Delivery",
            objective="fastest_delivery",
            orders=orders_fastest,
            constraints=constraints,
        )

        # ---------------------------------------------------------------------
        # Strategy 3: Minimum Suppliers (Consolidated to primary distributor)
        # ---------------------------------------------------------------------
        # Count frequency of each supplier across available offers
        supp_counts: Dict[str, int] = {}
        for off in compatible_offers:
            supp_counts[off.supplier_id] = supp_counts.get(off.supplier_id, 0) + 1

        primary_supp_id = max(supp_counts.items(), key=lambda x: x[1])[0] if supp_counts else None

        min_supp_selection: List[SupplierOffer] = []
        for b_item in bom_items:
            b_id = b_item.get("bom_item_id")
            avail_offers = offers_by_item.get(b_id, [])
            if avail_offers:
                # Prefer primary supplier if present, else fallback to cheapest
                pref = next((o for o in avail_offers if o.supplier_id == primary_supp_id), None)
                min_supp_selection.append(pref or avail_offers[0])

        orders_min_supp = await self.order_consolidator.consolidate_orders(
            min_supp_selection, bom_items, destination, shipping_mode="surface"
        )
        strat_min_supp = self._build_strategy(
            strat_id="STRAT-003",
            name="Minimum Number of Suppliers",
            objective="minimum_suppliers",
            orders=orders_min_supp,
            constraints=constraints,
        )

        # ---------------------------------------------------------------------
        # Strategy 4: Balanced Cost & Delivery
        # ---------------------------------------------------------------------
        orders_balanced = await self.order_consolidator.consolidate_orders(
            cheapest_selection, bom_items, destination, shipping_mode="express"
        )
        strat_balanced = self._build_strategy(
            strat_id="STRAT-004",
            name="Balanced Cost + Delivery",
            objective="balanced_cost_delivery",
            orders=orders_balanced,
            constraints=constraints,
        )

        all_strategies = [strat_cheapest, strat_fastest, strat_min_supp, strat_balanced]

        # Selected default strategy is Lowest Landed Cost (or fastest if delivery constraint strictly mandates)
        selected_strategy = strat_cheapest
        if constraints.maximum_delivery_days and strat_cheapest.estimated_delivery_days:
            if strat_cheapest.estimated_delivery_days > constraints.maximum_delivery_days:
                if strat_fastest.estimated_delivery_days and strat_fastest.estimated_delivery_days <= constraints.maximum_delivery_days:
                    selected_strategy = strat_fastest

        # Build OptimizedBOMItem records for selected strategy
        optimized_items: List[OptimizedBOMItem] = []
        for order in selected_strategy.orders:
            for item in order.items:
                # Find matching BOM metadata
                matching_bom = next((b for b in bom_items if b.get("bom_item_id") == item.bom_item_id), {})
                matching_offer = next((o for o in compatible_offers if o.bom_item_id == item.bom_item_id and o.supplier_id == order.supplier_id), None)

                optimized_items.append(
                    OptimizedBOMItem(
                        bom_item_id=item.bom_item_id,
                        selected_supplier=order.supplier_name,
                        selected_part_number=item.part_number,
                        manufacturer=matching_bom.get("manufacturer", "Manufacturer"),
                        category=matching_bom.get("category", "component"),
                        subsystem_id=matching_bom.get("subsystem_id", "SUB-GEN"),
                        required_quantity=item.required_quantity,
                        purchased_quantity=item.purchased_quantity,
                        unit_price=item.unit_price,
                        product_cost=item.product_cost,
                        shipping_cost_allocated=item.shipping_cost_allocated,
                        known_landed_cost=item.known_landed_cost,
                        stock_status=matching_offer.stock_status if matching_offer else "in_stock",
                        lead_time_days=matching_offer.lead_time_days if matching_offer else 2,
                        alternative_options=[],
                        selection_reason=f"Selected in '{selected_strategy.name}' strategy from {order.supplier_name}.",
                        confidence=0.96,
                    )
                )

        return selected_strategy, all_strategies, optimized_items

    def _build_strategy(
        self,
        strat_id: str,
        name: str,
        objective: str,
        orders: List[SupplierOrder],
        constraints: ProjectConstraints,
    ) -> ProcurementStrategy:
        total_prod = round(sum(o.product_subtotal for o in orders), 2)
        total_ship = round(sum(o.shipping_cost for o in orders), 2)
        total_landed = round(total_prod + total_ship, 2)
        max_delivery = max((o.delivery_estimate_days or 3) for o in orders) if orders else None

        warnings: List[str] = []
        constraints_sat = True

        if constraints.maximum_budget and total_landed > constraints.maximum_budget:
            constraints_sat = False
            warnings.append(
                f"Budget limit ₹{constraints.maximum_budget:,.2f} exceeded by ₹{total_landed - constraints.maximum_budget:,.2f}"
            )

        if constraints.maximum_delivery_days and max_delivery and max_delivery > constraints.maximum_delivery_days:
            constraints_sat = False
            warnings.append(
                f"Delivery timeframe ({max_delivery} days) exceeds maximum constraint ({constraints.maximum_delivery_days} days)"
            )

        return ProcurementStrategy(
            strategy_id=strat_id,
            name=name,
            objective=objective,
            orders=orders,
            total_product_cost=total_prod,
            total_shipping_cost=total_ship,
            total_known_landed_cost=total_landed,
            unknown_costs=[],
            supplier_count=len(orders),
            estimated_delivery_days=max_delivery,
            constraints_satisfied=constraints_sat,
            warnings=warnings,
        )
