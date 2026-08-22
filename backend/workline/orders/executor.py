"""Order Execution Engine coordinating vendor submission, manual checkout kits, and idempotency."""

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from backend.workline.orders.audit import OrderAuditLogger, order_audit_logger
from backend.workline.orders.models import (
    AuditEventType,
    Order,
    OrderExecutionMode,
    OrderStatus,
    PaymentSession,
    PaymentStatus,
    Receipt,
)
from backend.workline.orders.providers.procurement_service import CentralProcurementOrderService
from backend.workline.orders.receipts import ReceiptService


class OrderExecutor:
    """
    Executes approved orders with authorized payment proofs across automated vendor APIs
    or generates guided manual checkout packages.
    """

    def __init__(
        self,
        procurement_svc: Optional[CentralProcurementOrderService] = None,
        receipt_svc: Optional[ReceiptService] = None,
        audit_logger: Optional[OrderAuditLogger] = None,
    ):
        self.procurement_svc = procurement_svc or CentralProcurementOrderService()
        self.receipt_svc = receipt_svc or ReceiptService()
        self.audit_logger = audit_logger or order_audit_logger
        self._executed_idempotency_keys: Dict[str, Dict[str, Any]] = {}

    async def execute_order(
        self,
        order: Order,
        payment_session: PaymentSession,
    ) -> Tuple[bool, Order, Optional[Receipt], Optional[str]]:
        """
        Executes order fulfillment once payment authorization is cryptographically verified.
        Returns: (success, updated_order, receipt, error_message)
        """
        # 1. Verify Payment Precondition
        if payment_session.status not in (PaymentStatus.AUTHORIZED, PaymentStatus.SETTLED):
            return False, order, None, f"Payment is not authorized (status: {payment_session.status.value}). Execution blocked."

        # 2. Idempotency Check (Prevent duplicate vendor billing/orders)
        if order.idempotency_key in self._executed_idempotency_keys:
            cached = self._executed_idempotency_keys[order.idempotency_key]
            return True, cached["order"], cached.get("receipt"), None

        # 3. Transition to SUBMITTING
        prev_status = order.status
        order.status = OrderStatus.SUBMITTING
        now = datetime.now(timezone.utc).isoformat()
        order.submitted_at = now

        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.ORDER_SUBMITTING,
            actor_type="SYSTEM",
            actor_id="order_executor",
            previous_status=prev_status.value,
            new_status=order.status.value,
            metadata={"idempotency_key": order.idempotency_key},
        )

        # 4. Dispatch to Vendor Provider
        provider = self.procurement_svc.get_provider_for_vendor(order.vendor)
        success, resulting_status, ext_order_id, details = await provider.create_order(order)

        if not success:
            order.status = OrderStatus.FAILED
            await self.audit_logger.log_event(
                order_id=order.order_id,
                project_id=order.project_id,
                event_type=AuditEventType.ORDER_FAILED,
                actor_type="SYSTEM",
                actor_id="order_executor",
                previous_status=OrderStatus.SUBMITTING.value,
                new_status=OrderStatus.FAILED.value,
                metadata={"details": details},
            )
            return False, order, None, "Vendor order submission failed."

        # 5. Handle Resulting State
        order.status = resulting_status
        order.external_order_id = ext_order_id
        if resulting_status == OrderStatus.CONFIRMED:
            order.confirmed_at = now

        receipt = None
        if resulting_status == OrderStatus.CONFIRMED:
            receipt = await self.receipt_svc.generate_receipt(order, external_order_id=ext_order_id)
            order.receipt_id = receipt.receipt_id

            await self.audit_logger.log_event(
                order_id=order.order_id,
                project_id=order.project_id,
                event_type=AuditEventType.ORDER_CONFIRMED,
                actor_type="SYSTEM",
                actor_id="order_executor",
                previous_status=OrderStatus.SUBMITTING.value,
                new_status=OrderStatus.CONFIRMED.value,
                metadata={"external_order_id": ext_order_id, "receipt_id": receipt.receipt_id},
            )
        elif resulting_status == OrderStatus.MANUAL_CHECKOUT_REQUIRED:
            await self.audit_logger.log_event(
                order_id=order.order_id,
                project_id=order.project_id,
                event_type=AuditEventType.MANUAL_CHECKOUT_PREPARED,
                actor_type="SYSTEM",
                actor_id="order_executor",
                previous_status=OrderStatus.SUBMITTING.value,
                new_status=OrderStatus.MANUAL_CHECKOUT_REQUIRED.value,
                metadata={"checkout_url": details.get("checkout_url") if details else None},
            )

        # Cache in idempotency registry
        self._executed_idempotency_keys[order.idempotency_key] = {
            "order": order,
            "receipt": receipt,
        }

        return True, order, receipt, None
