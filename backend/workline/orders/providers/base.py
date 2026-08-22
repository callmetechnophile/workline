"""Procurement Order Provider interface for Workline order execution."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple

from backend.workline.orders.models import Order, OrderExecutionMode, OrderStatus, Receipt


class ProcurementOrderProvider(ABC):
    """Abstract interface defining required capabilities for placing vendor orders."""

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """Target vendor or marketplace name."""
        pass

    @property
    @abstractmethod
    def execution_mode(self) -> OrderExecutionMode:
        """Indicates whether vendor supports automated API orders or requires manual checkout."""
        pass

    @abstractmethod
    async def create_order(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, OrderStatus, Optional[str], Optional[Dict[str, Any]]]:
        """
        Execute order with vendor.
        Returns: (success, resulting_status, external_order_id, execution_details)
        """
        pass

    @abstractmethod
    async def get_order_status(self, external_order_id: str) -> OrderStatus:
        """Query vendor status for an placed order."""
        pass

    @abstractmethod
    async def cancel_order(self, external_order_id: str) -> bool:
        """Request order cancellation with vendor."""
        pass

    @abstractmethod
    async def get_receipt(self, order: Order, external_order_id: str) -> Optional[Receipt]:
        """Fetch official receipt / invoice."""
        pass
