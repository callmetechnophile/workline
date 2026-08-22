"""Procurement risk and price variation thresholds."""

from typing import Optional, Tuple
from backend.workline.orders.models import OrderPolicy, RevalidationReport


class RiskPolicyValidator:
    """Evaluates price slippage, component obsolescence, and stock availability risks."""

    def __init__(self, policy: Optional[OrderPolicy] = None):
        self.policy = policy or OrderPolicy()

    def evaluate_revalidation_risk(
        self, report: RevalidationReport, policy: Optional[OrderPolicy] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Determines whether price change requires invalidating previous approval.
        """
        pol = policy or self.policy

        if not report.is_valid:
            return False, "One or more components are out of stock or unavailable."

        # If total price increased beyond allowed threshold (e.g. 5%)
        if report.total_percentage_change > (pol.price_change_threshold * 100):
            return False, (
                f"Total order price increased by {report.total_percentage_change:.1f}%, which exceeds "
                f"the allowed price change threshold of {pol.price_change_threshold * 100:.1f}%. Re-approval required."
            )

        return True, None
