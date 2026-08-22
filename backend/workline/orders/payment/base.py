"""Generic Payment Provider interface for Workline financial transactions."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from backend.workline.orders.models import Order, PaymentRequest, PaymentSession, PaymentStatus


class PaymentProvider(ABC):
    """Abstract interface defining required capabilities for any payment authorization provider."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier name (e.g. 'x402', 'Mock')."""
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        """Check if provider is configured and available."""
        pass

    @abstractmethod
    async def create_payment_request(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentRequest:
        """Construct a standardized payment request requirement for an approved order."""
        pass

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Check status of a payment request or session."""
        pass

    @abstractmethod
    async def verify_payment(
        self, payment_id: str, signed_proof: Dict[str, Any]
    ) -> Tuple[bool, Optional[str], Optional[PaymentSession]]:
        """Verify client payment authorization and settle payment session."""
        pass

    @abstractmethod
    async def handle_payment_failure(self, payment_id: str, reason: str) -> bool:
        """Transition payment state to failed with explanation."""
        pass

    @abstractmethod
    async def handle_payment_expiry(self, payment_id: str) -> bool:
        """Expire a stale payment request."""
        pass
