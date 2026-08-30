"""
Order-level shipping and freight allocation service for BOMOptimizationAgent (Sections 13, 14, 26).
"""

from typing import List
from research_agents.bom_optimization_agent.adapters.shipping.base import ShippingCalculator
from research_agents.bom_optimization_agent.adapters.shipping.bluedart import BlueDartShippingProvider
from research_agents.bom_optimization_agent.schemas import Location, ShippingOption, SupplierOrder


class ShippingService:
    """Calculates order-level freight and allocates shipping cost across line items."""

    def __init__(self, shipping_calculator: ShippingCalculator = None):
        self.calculator = shipping_calculator or BlueDartShippingProvider()

    async def calculate_order_shipping(
        self,
        order: SupplierOrder,
        destination: Location,
        shipping_mode: str = "surface",
    ) -> ShippingOption:
        """
        Calculates shipping option for a consolidated supplier order.
        """
        # Estimate package weight: base 0.3 kg + 0.1 kg per line item
        estimated_weight = 0.3 + (len(order.items) * 0.1)

        ship_option = await self.calculator.calculate_shipping(
            supplier_id=order.supplier_id,
            origin=order.supplier_location,
            destination=destination,
            shipment_weight_kg=estimated_weight,
            shipping_mode=shipping_mode,
        )

        return ship_option

    def allocate_shipping_costs(self, order: SupplierOrder, shipping_cost: float) -> None:
        """
        Allocates order shipping cost proportionally across line items based on product value.
        """
        order.shipping_cost = shipping_cost
        order.known_landed_cost = round(order.product_subtotal + shipping_cost + order.additional_cost, 2)

        if not order.items:
            return

        total_val = sum(it.product_cost for it in order.items)

        if total_val > 0:
            for it in order.items:
                alloc = round(shipping_cost * (it.product_cost / total_val), 2)
                it.shipping_cost_allocated = alloc
                it.known_landed_cost = round(it.product_cost + alloc, 2)
        else:
            # Equal allocation fallback
            per_item = round(shipping_cost / len(order.items), 2)
            for it in order.items:
                it.shipping_cost_allocated = per_item
                it.known_landed_cost = round(it.product_cost + per_item, 2)
