"""Order tracking, delivery milestones, and status update orchestrator."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.workline.database.models import GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.orders.audit import OrderAuditLogger, order_audit_logger
from backend.workline.orders.models import AuditEventType, Order, OrderStatus


class OrderTracker:
    """Tracks order fulfillment lifecycle from submission to delivery."""

    def __init__(
        self,
        graph_repo: Optional[GraphRepository] = None,
        audit_logger: Optional[OrderAuditLogger] = None,
    ):
        self.graph_repo = graph_repo or GraphRepository()
        self.audit_logger = audit_logger or order_audit_logger

    async def update_status(
        self,
        order: Order,
        new_status: OrderStatus,
        actor_type: str = "SYSTEM",
        actor_id: str = "order_tracker",
        reason: Optional[str] = None,
    ) -> Order:
        """Update order status and log audit event."""
        prev = order.status
        order.status = new_status

        now = datetime.now(timezone.utc).isoformat()
        if new_status == OrderStatus.SUBMITTED:
            order.submitted_at = now
        elif new_status == OrderStatus.CONFIRMED:
            order.confirmed_at = now
        elif new_status == OrderStatus.CANCELLED:
            order.cancelled_at = now

        # 1. Audit log
        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.ORDER_CONFIRMED if new_status == OrderStatus.CONFIRMED else AuditEventType.ORDER_SUBMITTED,
            actor_type=actor_type,
            actor_id=actor_id,
            previous_status=prev.value,
            new_status=new_status.value,
            metadata={"reason": reason} if reason else {},
        )

        # 2. Update SurrealDB node
        try:
            await self.graph_repo.save_node(
                GraphNode(
                    id=order.order_id,
                    type="Order",
                    label=f"Order: {order.order_id} ({order.status.value})",
                    data={"project_id": order.project_id, **order.model_dump()},
                )
            )
        except Exception:
            pass

        return order
