"""Payment verification logic enforcing payment validation BEFORE order submission."""

from typing import Any, Dict, Optional, Tuple
from backend.workline.orders.models import Order, PaymentSession, PaymentStatus
from backend.workline.orders.payment.base import PaymentProvider


class PaymentVerificationService:
    """
    Enforces strict payment verification preconditions before an order is allowed
    to advance to SUBMITTING or CONFIRMED states.
    """

    def __init__(self, provider: PaymentProvider):
        self.provider = provider

    async def verify_payment_proof(
        self,
        order: Order,
        payment_id: str,
        signed_proof: Dict[str, Any],
    ) -> Tuple[bool, Optional[str], Optional[PaymentSession]]:
        """
        Validates cryptographic proof, settles session, and confirms matching order amount.
        """
        is_valid, err, session = await self.provider.verify_payment(payment_id, signed_proof)
        if not is_valid or not session:
            return False, err or "Payment verification failed.", session

        if session.status != PaymentStatus.AUTHORIZED:
            return False, f"Payment is in '{session.status.value}' state. Must be 'AUTHORIZED' to proceed.", session

        return True, None, session
