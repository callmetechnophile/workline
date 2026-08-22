"""Central Procurement Order Service dispatching to vendor-specific execution providers."""

from typing import Any, Dict, Optional, Tuple

from backend.workline.orders.models import (
    Order,
    OrderExecutionMode,
    OrderStatus,
    Receipt,
)
from backend.workline.orders.providers.base import ProcurementOrderProvider
from backend.workline.orders.providers.manual import ManualProcurementProvider
from backend.workline.orders.providers.vendor_api import VendorAPIProcurementProvider


class CentralProcurementOrderService(ProcurementOrderProvider):
    """
    Central dispatcher coordinating vendor orders based on whether a vendor has
    an automated order API (DigiKey/Mouser) or requires manual checkout (Robu/Robocraze).
    """

    def __init__(self):
        self._providers: Dict[str, ProcurementOrderProvider] = {
            "DigiKey": VendorAPIProcurementProvider(vendor_name="DigiKey"),
            "Mouser": VendorAPIProcurementProvider(vendor_name="Mouser"),
            "Robu": ManualProcurementProvider(vendor_name="Robu", checkout_base_url="https://robu.in/checkout"),
            "Robocraze": ManualProcurementProvider(vendor_name="Robocraze", checkout_base_url="https://robocraze.com/cart"),
        }
        self._fallback = ManualProcurementProvider(vendor_name="Generic Vendor")

    @property
    def vendor_name(self) -> str:
        return "Multi-Vendor Procurement Service"

    @property
    def execution_mode(self) -> OrderExecutionMode:
        return OrderExecutionMode.AUTOMATED

    def get_provider_for_vendor(self, vendor_name: str) -> ProcurementOrderProvider:
        """Resolve vendor adapter with explicit execution mode."""
        return self._providers.get(vendor_name, self._fallback)

    async def create_order(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, OrderStatus, Optional[str], Optional[Dict[str, Any]]]:
        provider = self.get_provider_for_vendor(order.vendor)
        return await provider.create_order(order, metadata)

    async def get_order_status(self, external_order_id: str) -> OrderStatus:
        for p in self._providers.values():
            status = await p.get_order_status(external_order_id)
            if status != OrderStatus.MANUAL_CHECKOUT_REQUIRED:
                return status
        return OrderStatus.CONFIRMED

    async def cancel_order(self, external_order_id: str) -> bool:
        for p in self._providers.values():
            if await p.cancel_order(external_order_id):
                return True
        return False

    async def get_receipt(self, order: Order, external_order_id: str) -> Optional[Receipt]:
        provider = self.get_provider_for_vendor(order.vendor)
        return await provider.get_receipt(order, external_order_id)
