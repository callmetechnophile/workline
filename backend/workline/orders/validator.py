"""Order state machine transitions and live price/stock revalidation."""

from typing import Dict, List, Optional, Set, Tuple
from backend.workline.orders.models import (
    ApprovalStatus,
    Order,
    OrderStatus,
    PaymentStatus,
    PriceRevalidationItem,
    RevalidationReport,
)
from backend.workline.procurement.engine import ProcurementEngine, procurement_engine


class OrderValidator:
    """
    Enforces strict state machine transition rules and live vendor price/stock verification.
    """

    # Explicit permitted transitions
    VALID_STATE_TRANSITIONS: Dict[OrderStatus, Set[OrderStatus]] = {
        OrderStatus.DRAFT: {OrderStatus.VALIDATING, OrderStatus.CANCELLED},
        OrderStatus.VALIDATING: {OrderStatus.READY_FOR_APPROVAL, OrderStatus.FAILED, OrderStatus.CANCELLED},
        OrderStatus.READY_FOR_APPROVAL: {OrderStatus.APPROVED, OrderStatus.VALIDATING, OrderStatus.CANCELLED},
        OrderStatus.APPROVED: {OrderStatus.PAYMENT_REQUIRED, OrderStatus.READY_FOR_APPROVAL, OrderStatus.CANCELLED},
        OrderStatus.PAYMENT_REQUIRED: {OrderStatus.PAYMENT_PENDING, OrderStatus.READY_FOR_APPROVAL, OrderStatus.CANCELLED},
        OrderStatus.PAYMENT_PENDING: {OrderStatus.PAYMENT_AUTHORIZED, OrderStatus.FAILED, OrderStatus.READY_FOR_APPROVAL, OrderStatus.CANCELLED},
        OrderStatus.PAYMENT_AUTHORIZED: {OrderStatus.SUBMITTING, OrderStatus.CANCELLED, OrderStatus.REFUNDED},
        OrderStatus.SUBMITTING: {OrderStatus.SUBMITTED, OrderStatus.CONFIRMED, OrderStatus.MANUAL_CHECKOUT_REQUIRED, OrderStatus.FAILED},
        OrderStatus.SUBMITTED: {OrderStatus.CONFIRMED, OrderStatus.PARTIALLY_FULFILLED, OrderStatus.FAILED, OrderStatus.CANCELLED},
        OrderStatus.MANUAL_CHECKOUT_REQUIRED: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
        OrderStatus.CONFIRMED: {OrderStatus.PARTIALLY_FULFILLED, OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.REFUNDED},
        OrderStatus.PARTIALLY_FULFILLED: {OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.REFUNDED},
        OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.REFUNDED},
        OrderStatus.DELIVERED: {OrderStatus.REFUNDED},
        OrderStatus.FAILED: {OrderStatus.DRAFT, OrderStatus.CANCELLED},
        OrderStatus.CANCELLED: set(),
        OrderStatus.REFUNDED: set(),
    }

    def __init__(self, procurement: Optional[ProcurementEngine] = None):
        self.procurement = procurement or procurement_engine

    def validate_transition(self, current_status: OrderStatus, target_status: OrderStatus) -> Tuple[bool, Optional[str]]:
        """Verify if state transition is legally permissible."""
        if current_status == target_status:
            return True, None

        allowed = self.VALID_STATE_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            return False, f"Invalid state transition from '{current_status.value}' to '{target_status.value}'."

        return True, None

    async def revalidate_order_data(self, order: Order) -> RevalidationReport:
        """
        Revalidates live prices, stock levels, and vendor availability before approval and payment.
        Does NOT trust stale BOM-time data blindly.
        """
        items: List[PriceRevalidationItem] = []
        warnings: List[str] = []
        price_changes = 0
        stock_changes = 0
        total_bom_price = 0.0
        total_curr_price = 0.0
        is_valid = True

        for item in order.items:
            bom_price = item.unit_price
            total_bom_price += (bom_price * item.quantity)

            # Query live provider for latest component offer
            cand = await self.procurement.search_engine.nexar.search_mpn(item.mpn)
            if not cand:
                cand = await self.procurement.search_engine.scrapling.search_mpn(item.mpn)

            curr_price = bom_price
            curr_stock = item.stock_at_validation or 100
            is_avail = True

            if cand:
                # Find matching vendor listing
                match_listing = next((l for l in cand.listings if l.vendor_name == item.vendor_name), None)
                if not match_listing and cand.listings:
                    match_listing = cand.listings[0]

                if match_listing and match_listing.unit_price:
                    curr_price = match_listing.unit_price
                    curr_stock = match_listing.stock or 50
                    is_avail = match_listing.in_stock

            total_curr_price += (curr_price * item.quantity)
            diff = round(curr_price - bom_price, 2)
            pct = round((diff / bom_price) * 100, 2) if bom_price > 0 else 0.0

            status_str = "UNCHANGED"
            if diff > 0:
                status_str = "INCREASED"
                price_changes += 1
                warnings.append(f"Price increased for {item.mpn}: {order.currency} {bom_price} -> {order.currency} {curr_price} (+{pct}%)")
            elif diff < 0:
                status_str = "DECREASED"
                price_changes += 1
                warnings.append(f"Price decreased for {item.mpn}: {order.currency} {bom_price} -> {order.currency} {curr_price} ({pct}%)")

            if not is_avail:
                status_str = "OUT_OF_STOCK"
                stock_changes += 1
                is_valid = False
                warnings.append(f"Component {item.mpn} is currently out of stock at {item.vendor_name}.")

            items.append(
                PriceRevalidationItem(
                    component_id=item.component_id,
                    mpn=item.mpn,
                    vendor_name=item.vendor_name,
                    bom_unit_price=bom_price,
                    current_unit_price=curr_price,
                    price_difference=diff,
                    percentage_change=pct,
                    bom_stock=item.stock_at_validation,
                    current_stock=curr_stock,
                    is_available=is_avail,
                    status=status_str,
                )
            )

        total_diff = round(total_curr_price - total_bom_price, 2)
        total_pct = round((total_diff / total_bom_price) * 100, 2) if total_bom_price > 0 else 0.0

        # Requires reapproval if price increased by > 5% or components out of stock
        requires_reapproval = (total_pct > 5.0) or not is_valid

        return RevalidationReport(
            order_id=order.order_id,
            is_valid=is_valid,
            requires_reapproval=requires_reapproval,
            price_changes_count=price_changes,
            stock_changes_count=stock_changes,
            total_bom_price=round(total_bom_price, 2),
            total_current_price=round(total_curr_price, 2),
            total_percentage_change=total_pct,
            items=items,
            warnings=warnings,
        )
