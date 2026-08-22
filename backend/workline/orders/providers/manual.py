"""Manual Checkout Provider for vendors without automated order APIs (e.g. Robu, Robocraze)."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple
import uuid

from backend.workline.orders.models import (
    ManualCheckoutPackage,
    Order,
    OrderExecutionMode,
    OrderStatus,
    Receipt,
    ReceiptVerificationStatus,
)
from backend.workline.orders.providers.base import ProcurementOrderProvider


class ManualProcurementProvider(ProcurementOrderProvider):
    """
    Handles vendors that lack automated checkout APIs by creating a structured
    Order Package and guiding the user to complete external checkout.
    """

    def __init__(self, vendor_name: str = "Robu", checkout_base_url: Optional[str] = None):
        self._vendor_name = vendor_name
        self.checkout_base_url = checkout_base_url or f"https://{vendor_name.lower()}.in/cart"
        self._packages: Dict[str, ManualCheckoutPackage] = {}

    @property
    def vendor_name(self) -> str:
        return self._vendor_name

    @property
    def execution_mode(self) -> OrderExecutionMode:
        return OrderExecutionMode.MANUAL

    async def create_order(
        self, order: Order, metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, OrderStatus, Optional[str], Optional[Dict[str, Any]]]:
        """Generate structured manual checkout package and transition order to MANUAL_CHECKOUT_REQUIRED."""
        pkg_id = f"pkg_{uuid.uuid4().hex[:8]}"
        pkg = ManualCheckoutPackage(
            package_id=pkg_id,
            order_id=order.order_id,
            vendor=order.vendor,
            items=order.items,
            subtotal=order.subtotal,
            shipping=order.shipping_cost,
            total=order.total,
            currency=order.currency,
            checkout_url=self.checkout_base_url,
            instructions=[
                f"1. Open vendor checkout page: {self.checkout_base_url}",
                f"2. Add {len(order.items)} verified component item(s) to basket.",
                f"3. Apply shipping address and complete vendor payment of {order.currency} {order.total:.2f}.",
                "4. Upload order confirmation number or invoice receipt in Workline.",
            ],
        )

        self._packages[order.order_id] = pkg
        ext_order_id = f"MANUAL-{order.order_id}"

        details = {
            "execution_mode": "MANUAL",
            "package_id": pkg_id,
            "checkout_url": pkg.checkout_url,
            "instructions": pkg.instructions,
        }

        return True, OrderStatus.MANUAL_CHECKOUT_REQUIRED, ext_order_id, details

    async def get_order_status(self, external_order_id: str) -> OrderStatus:
        return OrderStatus.MANUAL_CHECKOUT_REQUIRED

    async def cancel_order(self, external_order_id: str) -> bool:
        return True

    async def get_receipt(self, order: Order, external_order_id: str) -> Optional[Receipt]:
        return Receipt(
            receipt_id=f"rec_man_{uuid.uuid4().hex[:8]}",
            order_id=order.order_id,
            vendor=order.vendor,
            external_order_id=external_order_id,
            subtotal=order.subtotal,
            shipping=order.shipping_cost,
            total=order.total,
            currency=order.currency,
            source="Manual Vendor Receipt Upload",
            verification_status=ReceiptVerificationStatus.UNVERIFIED,
        )
