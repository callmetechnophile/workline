"""Central Order Service: Coordinates Order Plans, Preview, Human Approval, Payment, and Execution."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import uuid

from cli.wline.core.paths import get_config_dir
from backend.workline.database.models import GraphEdge, GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.orders.audit import OrderAuditLogger, order_audit_logger
from backend.workline.orders.executor import OrderExecutor
from backend.workline.orders.models import (
    ApprovalStatus,
    AuditEventType,
    CostBreakdownItem,
    Order,
    OrderItem,
    OrderPlan,
    OrderPolicy,
    OrderStatus,
    OrderTotal,
    PaymentRequest,
    PaymentSession,
    PaymentStatus,
    Receipt,
    RevalidationReport,
)
from backend.workline.orders.payment.base import PaymentProvider
from backend.workline.orders.payment.mock import MockPaymentProvider
from backend.workline.orders.payment.session import PaymentSessionManager
from backend.workline.orders.payment.verification import PaymentVerificationService
from backend.workline.orders.payment.x402 import X402PaymentProvider
from backend.workline.orders.policies.approval import ApprovalPolicyValidator
from backend.workline.orders.policies.limits import SpendingLimitValidator
from backend.workline.orders.policies.risk import RiskPolicyValidator
from backend.workline.orders.receipts import ReceiptService
from backend.workline.orders.tracker import OrderTracker
from backend.workline.orders.validator import OrderValidator
from backend.workline.procurement.engine import ProcurementEngine, procurement_engine
from backend.workline.procurement.models import BOM, BOMStatus


class OrderService:
    """Central orchestrator for the entire Workline ordering and payment authorization lifecycle."""

    def __init__(
        self,
        procurement: Optional[ProcurementEngine] = None,
        graph_repo: Optional[GraphRepository] = None,
        project_repo: Optional[ProjectRepository] = None,
        payment_provider: Optional[PaymentProvider] = None,
        audit_logger: Optional[OrderAuditLogger] = None,
    ):
        self.procurement = procurement or procurement_engine
        self.graph_repo = graph_repo or GraphRepository()
        self.project_repo = project_repo or ProjectRepository()
        self.payment_provider = payment_provider or X402PaymentProvider()
        self.audit_logger = audit_logger or order_audit_logger

        self.validator = OrderValidator(procurement=self.procurement)
        self.spending_validator = SpendingLimitValidator()
        self.approval_validator = ApprovalPolicyValidator()
        self.risk_validator = RiskPolicyValidator()

        self.session_manager = PaymentSessionManager(graph_repo=self.graph_repo)
        self.payment_verifier = PaymentVerificationService(provider=self.payment_provider)
        self.receipt_service = ReceiptService(graph_repo=self.graph_repo)
        self.executor = OrderExecutor(receipt_svc=self.receipt_service, audit_logger=self.audit_logger)
        self.tracker = OrderTracker(graph_repo=self.graph_repo, audit_logger=self.audit_logger)

        self._plans: Dict[str, OrderPlan] = {}
        self._orders: Dict[str, Order] = {}
        self._order_dir = get_config_dir() / "orders"
        self._order_dir.mkdir(parents=True, exist_ok=True)

    # ==================== DISK PERSISTENCE FOR CLI ====================

    def _save_order_disk(self, order: Order) -> None:
        """Persist order JSON for cross-process CLI availability."""
        try:
            with open(self._order_dir / f"{order.order_id.replace(':', '_')}.json", "w", encoding="utf-8") as fp:
                fp.write(order.model_dump_json(indent=2))
        except Exception:
            pass

    def _load_order_disk(self, order_id: str) -> Optional[Order]:
        """Load order JSON from disk cache."""
        clean_id = order_id.replace(":", "_")
        fpath = self._order_dir / f"{clean_id}.json"
        if fpath.exists():
            try:
                with open(fpath, "r", encoding="utf-8") as fp:
                    return Order.model_validate_json(fp.read())
            except Exception:
                pass
        return None

    # ==================== 1. CREATE ORDER PLAN FROM BOM ====================

    async def create_order_plan(self, project_id: str, bom_id_or_name: str) -> OrderPlan:
        """Constructs an itemized OrderPlan from an approved or validated BOM."""
        bom = await self.procurement.get_bom(bom_id_or_name)
        if not bom:
            # Fallback check project id
            bom = await self.procurement.get_bom(project_id)

        if not bom:
            raise ValueError(f"No BOM found for '{bom_id_or_name}'. Run 'wline bom generate' first.")

        plan_id = f"plan_{uuid.uuid4().hex[:8]}"
        vendors = list({item.selected_vendor for item in bom.items})

        # Build OrderItems
        order_items: List[OrderItem] = []
        for i in bom.items:
            order_items.append(
                OrderItem(
                    order_item_id=f"ord_item_{uuid.uuid4().hex[:6]}",
                    order_id="",  # Will be populated on order creation
                    component_id=i.component_id,
                    bom_item_id=i.bom_item_id,
                    manufacturer=i.manufacturer,
                    mpn=i.mpn,
                    description=i.description,
                    quantity=i.quantity,
                    unit_price=i.unit_price,
                    currency=i.currency,
                    extended_price=i.extended_price,
                    vendor_listing_id=i.selected_listing_id,
                    vendor_name=i.selected_vendor,
                    product_url=i.vendor_product_url,
                    stock_at_validation=i.stock,
                    lead_time_at_validation=i.lead_time_days,
                    datasheet_id=i.datasheet_url,
                )
            )

        subtotal_val = round(sum(i.extended_price for i in order_items), 2)
        shipping_val = round(bom.estimated_shipping, 2)
        tax_val = round(subtotal_val * 0.18, 2)  # Standard 18% GST estimate
        fees_val = 0.0
        total_val = round(subtotal_val + shipping_val + tax_val + fees_val, 2)

        financials = OrderTotal(
            subtotal=CostBreakdownItem(value=subtotal_val, currency=bom.currency, status="VERIFIED"),
            shipping=CostBreakdownItem(value=shipping_val, currency=bom.currency, status="ESTIMATED"),
            tax=CostBreakdownItem(value=tax_val, currency=bom.currency, status="ESTIMATED"),
            fees=CostBreakdownItem(value=fees_val, currency=bom.currency, status="CONFIRMED"),
            total=CostBreakdownItem(value=total_val, currency=bom.currency, status="ESTIMATED"),
            currency=bom.currency,
        )

        plan = OrderPlan(
            plan_id=plan_id,
            project_id=project_id,
            bom_id=bom.bom_id,
            selected_vendors=vendors,
            selected_listings=[i.vendor_listing_id for i in order_items if i.vendor_listing_id],
            items=order_items,
            financials=financials,
            currency=bom.currency,
            data_freshness="FRESH",
            vendor_availability={v: True for v in vendors},
        )

        self._plans[plan_id] = plan
        return plan

    # ==================== 2. CREATE ORDERS FROM PLAN ====================

    async def create_orders_from_plan(
        self,
        plan: OrderPlan,
        user_id: str = "user:engineer",
        team_id: str = "team:default",
        user_role: str = "ENGINEER",
    ) -> List[Order]:
        """Splits an OrderPlan into per-vendor Order entities in READY_FOR_APPROVAL status."""
        if not self.approval_validator.can_create_order(user_role):
            raise PermissionError(f"User role '{user_role}' cannot create orders.")

        orders_created: List[Order] = []
        vendor_grouped: Dict[str, List[OrderItem]] = {}

        for item in plan.items:
            vendor_grouped.setdefault(item.vendor_name, []).append(item)

        for vendor_name, v_items in vendor_grouped.items():
            order_id = f"WL-ORD-{uuid.uuid4().hex[:6].upper()}"
            sub = round(sum(i.extended_price for i in v_items), 2)
            est_ship = self.procurement.optimizer.shipping_calc.estimate_shipping(vendor_name, sub).estimated_cost
            tax = round(sub * 0.18, 2)
            fees = 0.0
            tot = round(sub + est_ship + tax + fees, 2)

            # Assign order_id to items
            for i in v_items:
                i.order_id = order_id

            v_financials = OrderTotal(
                subtotal=CostBreakdownItem(value=sub, currency=plan.currency, status="VERIFIED"),
                shipping=CostBreakdownItem(value=est_ship, currency=plan.currency, status="ESTIMATED"),
                tax=CostBreakdownItem(value=tax, currency=plan.currency, status="ESTIMATED"),
                fees=CostBreakdownItem(value=fees, currency=plan.currency, status="CONFIRMED"),
                total=CostBreakdownItem(value=tot, currency=plan.currency, status="ESTIMATED"),
                currency=plan.currency,
            )

            provider = self.executor.procurement_svc.get_provider_for_vendor(vendor_name)
            exec_mode = provider.execution_mode

            order = Order(
                order_id=order_id,
                project_id=plan.project_id,
                bom_id=plan.bom_id,
                procurement_plan_id=plan.plan_id,
                user_id=user_id,
                team_id=team_id,
                vendor=vendor_name,
                currency=plan.currency,
                subtotal=sub,
                shipping_cost=est_ship,
                tax=tax,
                fees=fees,
                total=tot,
                financials=v_financials,
                items=v_items,
                status=OrderStatus.READY_FOR_APPROVAL,
                payment_status=PaymentStatus.REQUIRED,
                approval_status=ApprovalStatus.PENDING,
                execution_mode=exec_mode,
                idempotency_key=f"idemp_{order_id}_{plan.version}",
            )

            self._orders[order_id] = order
            self._save_order_disk(order)
            orders_created.append(order)

            # 1. Audit log
            await self.audit_logger.log_event(
                order_id=order.order_id,
                project_id=order.project_id,
                event_type=AuditEventType.ORDER_CREATED,
                user_id=user_id,
                team_id=team_id,
                new_status=order.status.value,
                metadata={"vendor": vendor_name, "total": tot, "item_count": len(v_items)},
            )

            # 2. Persist to SurrealDB graph
            await self._persist_order_graph(order)

        return orders_created

    async def _persist_order_graph(self, order: Order) -> None:
        """Persists Order and OrderItem nodes with graph relationships."""
        # 1. Order Node
        await self.graph_repo.save_node(
            GraphNode(
                id=order.order_id,
                type="Order",
                label=f"Order: {order.order_id} ({order.vendor})",
                data={"project_id": order.project_id, **order.model_dump()},
            )
        )
        # Project -[HAS_ORDER]-> Order
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"has_ord:{order.project_id}_{order.order_id.replace(':', '_')}",
                source_id=f"project:{order.project_id}",
                target_id=order.order_id,
                relationship="HAS_ORDER",
                data={"project_id": order.project_id},
            )
        )
        # Order -[FOR_VENDOR]-> Vendor
        await self.graph_repo.save_edge(
            GraphEdge(
                id=f"for_vend:{order.order_id.replace(':', '_')}_{order.vendor}",
                source_id=order.order_id,
                target_id=f"vendor:{order.vendor}",
                relationship="FOR_VENDOR",
                data={"project_id": order.project_id},
            )
        )

        # 2. OrderItem Nodes and CONTAINS / REFERENCES edges
        for item in order.items:
            item_node_id = f"item:{item.order_item_id}"
            await self.graph_repo.save_node(
                GraphNode(
                    id=item_node_id,
                    type="OrderItem",
                    label=f"{item.mpn} (Qty: {item.quantity})",
                    data={"project_id": order.project_id, **item.model_dump()},
                )
            )
            # Order -[CONTAINS]-> OrderItem
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"contains_item:{order.order_id.replace(':', '_')}_{item.order_item_id}",
                    source_id=order.order_id,
                    target_id=item_node_id,
                    relationship="CONTAINS",
                    data={"project_id": order.project_id},
                )
            )
            # OrderItem -[REFERENCES]-> Component
            await self.graph_repo.save_edge(
                GraphEdge(
                    id=f"ref_comp:{item.order_item_id}_{item.component_id.replace(':', '_')}",
                    source_id=item_node_id,
                    target_id=item.component_id,
                    relationship="REFERENCES",
                    data={"project_id": order.project_id},
                )
            )

    # ==================== 3. GET ORDER & REVALIDATE ====================

    async def get_order(self, order_id: str) -> Optional[Order]:
        """Fetch order from memory or disk cache."""
        if order_id in self._orders:
            return self._orders[order_id]
        order = self._load_order_disk(order_id)
        if order:
            self._orders[order_id] = order
            return order
        return None

    async def revalidate_order(self, order_id: str) -> Tuple[Order, RevalidationReport]:
        """Run live price/stock revalidation on an order."""
        order = await self.get_order(order_id)
        if not order:
            raise ValueError(f"Order '{order_id}' not found.")

        report = await self.validator.revalidate_order_data(order)
        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.PRICE_REVALIDATED,
            previous_status=order.status.value,
            new_status=order.status.value,
            metadata={"price_changes": report.price_changes_count, "stock_changes": report.stock_changes_count},
        )
        return order, report

    # ==================== 4. HUMAN APPROVAL ====================

    async def approve_order(
        self,
        order_id: str,
        user_role: str = "OWNER",
        approved_by: str = "Lead Systems Engineer",
        is_agent: bool = False,
    ) -> Tuple[bool, Order, Optional[str]]:
        """Human approval checkpoint transitioning order from READY_FOR_APPROVAL to APPROVED."""
        order = await self.get_order(order_id)
        if not order:
            return False, order, f"Order '{order_id}' not found."

        # 1. Verify Role Authority (Agents strictly forbidden)
        can_approve, err = self.approval_validator.can_approve_order(user_role, is_agent=is_agent)
        if not can_approve:
            return False, order, err

        # 2. Revalidate live prices/stock before approving
        _, report = await self.revalidate_order(order_id)
        if not report.is_valid:
            return False, order, "Order cannot be approved: components are out of stock."

        # 3. Check Spending Limits
        ok_limits, limit_err = self.spending_validator.validate_spending_limits(order)
        if not ok_limits:
            return False, order, limit_err

        # 4. State transition
        can_trans, trans_err = self.validator.validate_transition(order.status, OrderStatus.APPROVED)
        if not can_trans:
            return False, order, trans_err

        now = datetime.now(timezone.utc).isoformat()
        order.status = OrderStatus.APPROVED
        order.approval_status = ApprovalStatus.APPROVED
        order.approved_at = now
        order.approved_by = approved_by
        order.payment_status = PaymentStatus.REQUIRED

        self._save_order_disk(order)

        # Audit log
        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.USER_APPROVED,
            actor_type="USER",
            actor_id=approved_by,
            previous_status=OrderStatus.READY_FOR_APPROVAL.value,
            new_status=OrderStatus.APPROVED.value,
            metadata={"approved_by": approved_by, "user_role": user_role},
        )

        # Update SurrealDB
        await self.graph_repo.save_node(
            GraphNode(
                id=order.order_id,
                type="Order",
                label=f"Order: {order.order_id} (APPROVED)",
                data={"project_id": order.project_id, **order.model_dump()},
            )
        )

        return True, order, None

    # ==================== 5. PAYMENT AUTHORIZATION (x402) ====================

    async def create_payment_request(self, order_id: str) -> Tuple[bool, Optional[PaymentRequest], Optional[str]]:
        """Constructs an x402 payment challenge for an approved order."""
        order = await self.get_order(order_id)
        if not order:
            return False, None, f"Order '{order_id}' not found."

        if order.status not in (OrderStatus.APPROVED, OrderStatus.PAYMENT_REQUIRED):
            return False, None, f"Order must be in APPROVED or PAYMENT_REQUIRED status (current: {order.status.value})."

        req = await self.payment_provider.create_payment_request(order)
        order.status = OrderStatus.PAYMENT_PENDING
        order.payment_status = PaymentStatus.PENDING
        self._save_order_disk(order)

        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.PAYMENT_REQUEST_CREATED,
            previous_status=OrderStatus.APPROVED.value,
            new_status=OrderStatus.PAYMENT_PENDING.value,
            metadata={"payment_request_id": req.payment_request_id, "amount": req.amount, "asset": req.asset},
        )

        return True, req, None

    async def verify_payment_and_execute(
        self,
        order_id: str,
        payment_id: str,
        signed_proof: Dict[str, Any],
    ) -> Tuple[bool, Order, Optional[Receipt], Optional[str]]:
        """
        Verifies cryptographic payment authorization proof and advances to order execution.
        """
        order = await self.get_order(order_id)
        if not order:
            return False, order, None, f"Order '{order_id}' not found."

        # 1. Verify Payment with Payment Provider
        valid_pay, pay_err, session = await self.payment_verifier.verify_payment_proof(order, payment_id, signed_proof)
        if not valid_pay or not session:
            order.payment_status = PaymentStatus.FAILED
            self._save_order_disk(order)
            await self.audit_logger.log_event(
                order_id=order.order_id,
                project_id=order.project_id,
                event_type=AuditEventType.PAYMENT_FAILED,
                metadata={"reason": pay_err},
            )
            return False, order, None, pay_err

        # 2. Payment Authorized
        order.payment_status = PaymentStatus.AUTHORIZED
        order.payment_authorized_at = datetime.now(timezone.utc).isoformat()
        order.status = OrderStatus.PAYMENT_AUTHORIZED
        self._save_order_disk(order)

        await self.session_manager.persist_session_graph(session, order.project_id)
        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.PAYMENT_AUTHORIZED,
            previous_status=OrderStatus.PAYMENT_PENDING.value,
            new_status=OrderStatus.PAYMENT_AUTHORIZED.value,
            metadata={"tx_hash": session.external_payment_id, "amount": session.amount},
        )

        # 3. Order Execution
        exec_ok, updated_order, receipt, exec_err = await self.executor.execute_order(order, session)
        self._save_order_disk(updated_order)
        return exec_ok, updated_order, receipt, exec_err

    # ==================== 6. CANCEL ORDER ====================

    async def cancel_order(self, order_id: str, reason: str = "User cancelled") -> Tuple[bool, Order, Optional[str]]:
        """Safely cancel an order."""
        order = await self.get_order(order_id)
        if not order:
            return False, order, f"Order '{order_id}' not found."

        can_trans, err = self.validator.validate_transition(order.status, OrderStatus.CANCELLED)
        if not can_trans:
            return False, order, err

        prev = order.status
        order.status = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc).isoformat()
        self._save_order_disk(order)

        await self.audit_logger.log_event(
            order_id=order.order_id,
            project_id=order.project_id,
            event_type=AuditEventType.ORDER_CANCELLED,
            previous_status=prev.value,
            new_status=OrderStatus.CANCELLED.value,
            metadata={"reason": reason},
        )
        return True, order, None


# Global order service singleton
order_service = OrderService()
