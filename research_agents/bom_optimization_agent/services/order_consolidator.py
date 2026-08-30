"""
Order consolidation and supplier bundling optimizer for BOMOptimizationAgent (Sections 19 & 20).
"""

from typing import Dict, List
import uuid
from research_agents.bom_optimization_agent.schemas import (
    Location,
    OrderItem,
    SupplierOffer,
    SupplierOrder,
)
from research_agents.bom_optimization_agent.services.price_calculator import PriceCalculator
from research_agents.bom_optimization_agent.services.shipping_service import ShippingService


class OrderConsolidator:
    """Consolidates selected supplier items into order bundles and applies shipping calculations."""

    def __init__(
        self,
        price_calculator: PriceCalculator = None,
        shipping_service: ShippingService = None,
    ):
        self.price_calculator = price_calculator or PriceCalculator()
        self.shipping_service = shipping_service or ShippingService()

    async def consolidate_orders(
        self,
        selected_offers: List[SupplierOffer],
        bom_items: List[Dict],
        destination: Location,
        shipping_mode: str = "surface",
    ) -> List[SupplierOrder]:
        """
        Groups selected component offers by supplier, calculates order product subtotals,
        and computes shipping costs per supplier order.
        """
        bom_name_map = {item.get("bom_item_id"): item.get("component_name", "Component") for item in bom_items}
        bom_qty_map = {item.get("bom_item_id"): int(item.get("quantity", 1)) for item in bom_items}

        # Group offers by supplier_id
        grouped: Dict[str, List[SupplierOffer]] = {}
        for offer in selected_offers:
            grouped.setdefault(offer.supplier_id, []).append(offer)

        orders: List[SupplierOrder] = []

        for supp_id, offers in grouped.items():
            first_offer = offers[0]
            order_items: List[OrderItem] = []
            subtotal = 0.0

            for off in offers:
                comp_name = bom_name_map.get(off.bom_item_id, "Component")
                req_qty = bom_qty_map.get(off.bom_item_id, 1)
                order_item, _ = self.price_calculator.calculate_item_cost(off, comp_name, req_qty)
                order_items.append(order_item)
                subtotal += order_item.product_cost

            order = SupplierOrder(
                order_id=f"ORD-{uuid.uuid4().hex[:6].upper()}",
                supplier_id=supp_id,
                supplier_name=first_offer.supplier_name,
                supplier_location=first_offer.location,
                items=order_items,
                product_subtotal=round(subtotal, 2),
                shipping_cost=0.0,
                additional_cost=0.0,
                known_landed_cost=round(subtotal, 2),
                unknown_costs=[],
                delivery_estimate_days=first_offer.lead_time_days or 3,
                shipping_mode=shipping_mode,
                carrier="Blue Dart",
                confidence=0.95,
            )

            # Compute and allocate shipping
            ship_opt = await self.shipping_service.calculate_order_shipping(order, destination, shipping_mode)
            lead_time = first_offer.lead_time_days or 1
            transit_time = ship_opt.estimated_delivery_days or 2
            order.delivery_estimate_days = lead_time + transit_time

            self.shipping_service.allocate_shipping_costs(order, ship_opt.shipping_cost or 100.0)
            orders.append(order)

        return orders
