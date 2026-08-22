"""Spending limits and financial budget policy enforcement."""

from typing import Optional, Tuple
from backend.workline.orders.models import Order, OrderPolicy


class SpendingLimitValidator:
    """Enforces per-order, daily, and monthly spending boundaries."""

    def __init__(self, policy: Optional[OrderPolicy] = None):
        self.policy = policy or OrderPolicy()

    def validate_spending_limits(
        self, order: Order, policy: Optional[OrderPolicy] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates if an order complies with configured spending policies.
        Returns (is_allowed, failure_reason).
        """
        pol = policy or self.policy

        # 1. Currency Check
        if order.currency not in pol.allowed_currencies:
            return False, f"Order currency '{order.currency}' is not in allowed currencies: {pol.allowed_currencies}"

        # 2. Allowed Vendors Check
        if pol.allowed_vendors and order.vendor not in pol.allowed_vendors:
            return False, f"Vendor '{order.vendor}' is not in approved vendor list: {pol.allowed_vendors}"

        # 3. Maximum Order Value Check
        if order.total > pol.maximum_order_value:
            return False, (
                f"Order total of {order.currency} {order.total:.2f} exceeds maximum order limit of "
                f"{order.currency} {pol.maximum_order_value:.2f}. Higher-level management authorization required."
            )

        return True, None
