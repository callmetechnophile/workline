"""
Deterministic price, MOQ, and volume tier calculation service for BOMOptimizationAgent (Sections 12, 27, 28).
"""

from typing import Tuple
from research_agents.bom_optimization_agent.schemas import OrderItem, SupplierOffer


class PriceCalculator:
    """Calculates deterministic component product subtotal respecting MOQs and price tiers."""

    def calculate_item_cost(
        self,
        offer: SupplierOffer,
        component_name: str,
        required_quantity: int,
    ) -> Tuple[OrderItem, bool]:
        """
        Calculates item-level product cost.

        Returns:
            Tuple of (OrderItem, is_fully_in_stock)
        """
        moq = offer.minimum_order_quantity or 1
        purchased_qty = max(required_quantity, moq)
        surplus_qty = purchased_qty - required_quantity
        moq_reason = f"Supplier MOQ is {moq} units" if surplus_qty > 0 else None

        # Determine unit price based on price breaks if provided
        unit_price = offer.unit_price or 0.0
        if offer.price_breaks:
            # Sort tiers descending by quantity threshold
            sorted_tiers = sorted(offer.price_breaks.items(), key=lambda x: int(x[0]), reverse=True)
            for threshold, tier_price in sorted_tiers:
                if purchased_qty >= int(threshold):
                    unit_price = tier_price
                    break

        product_subtotal = round(unit_price * purchased_qty, 2)

        # Check stock sufficiency
        in_stock = True
        if offer.available_quantity is not None and offer.available_quantity < purchased_qty:
            in_stock = False

        order_item = OrderItem(
            bom_item_id=offer.bom_item_id,
            part_number=offer.part_number,
            component_name=component_name,
            required_quantity=required_quantity,
            purchased_quantity=purchased_qty,
            surplus_quantity=surplus_qty,
            unit_price=unit_price,
            product_cost=product_subtotal,
            shipping_cost_allocated=None,
            known_landed_cost=product_subtotal,
            moq_reason=moq_reason,
        )

        return order_item, in_stock
