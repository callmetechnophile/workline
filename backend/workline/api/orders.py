"""FastAPI router for Workline Item Ordering and lifecycle management."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workline.orders.models import (
    Order,
    OrderPlan,
    OrderStatus,
    PaymentRequest,
    Receipt,
    RevalidationReport,
)
from backend.workline.orders.service import order_service


router = APIRouter(prefix="/api/orders", tags=["Workline Orders"])


class CreateOrderPlanRequest(BaseModel):
    project_id: str
    bom_id: str
    user_id: Optional[str] = "user:engineer"
    team_id: Optional[str] = "team:default"


class CreateOrdersRequest(BaseModel):
    plan_id: str
    user_id: Optional[str] = "user:engineer"
    team_id: Optional[str] = "team:default"
    user_role: Optional[str] = "ENGINEER"


class ApproveOrderRequest(BaseModel):
    approved_by: str = "Lead Systems Engineer"
    user_role: str = "OWNER"


class CancelOrderRequest(BaseModel):
    reason: str = "User requested cancellation"


@router.post("/plan", response_model=OrderPlan)
async def create_order_plan_api(payload: CreateOrderPlanRequest):
    """Generate an itemized OrderPlan from an approved BOM."""
    try:
        plan = await order_service.create_order_plan(payload.project_id, payload.bom_id)
        return plan
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Order plan creation failed: {str(exc)}")


@router.post("", response_model=List[Order])
async def create_orders_api(payload: CreateOrdersRequest):
    """Create vendor-specific Order records from an OrderPlan."""
    try:
        plan = order_service._plans.get(payload.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail=f"Plan '{payload.plan_id}' not found.")

        orders = await order_service.create_orders_from_plan(
            plan,
            user_id=payload.user_id or "user:engineer",
            team_id=payload.team_id or "team:default",
            user_role=payload.user_role or "ENGINEER",
        )
        return orders
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Order creation failed: {str(exc)}")


@router.get("/{order_id}", response_model=Order)
async def get_order_api(order_id: str):
    """Fetch order details."""
    order = await order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found.")
    return order


@router.post("/{order_id}/validate", response_model=RevalidationReport)
async def validate_order_api(order_id: str):
    """Revalidate live prices and stock availability for an order."""
    try:
        _, report = await order_service.revalidate_order(order_id)
        return report
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{order_id}/approve", response_model=Order)
async def approve_order_api(order_id: str, payload: ApproveOrderRequest):
    """Human approval checkpoint transitioning order from READY_FOR_APPROVAL to APPROVED."""
    ok, order, err = await order_service.approve_order(
        order_id,
        user_role=payload.user_role,
        approved_by=payload.approved_by,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    return order


@router.post("/{order_id}/cancel", response_model=Order)
async def cancel_order_api(order_id: str, payload: CancelOrderRequest):
    """Cancel an active order."""
    ok, order, err = await order_service.cancel_order(order_id, reason=payload.reason)
    if not ok:
        raise HTTPException(status_code=400, detail=err)
    return order


@router.post("/{order_id}/payment", response_model=PaymentRequest)
async def create_payment_request_api(order_id: str):
    """Construct an x402 payment challenge for an approved order."""
    ok, req, err = await order_service.create_payment_request(order_id)
    if not ok or not req:
        raise HTTPException(status_code=400, detail=err)
    return req


@router.get("/{order_id}/payment")
async def get_order_payment_api(order_id: str):
    """Fetch payment session status for an order."""
    session = order_service.session_manager.get_session(order_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"No payment session found for order '{order_id}'.")
    return session.model_dump()


@router.get("/{order_id}/receipt", response_model=Receipt)
async def get_order_receipt_api(order_id: str):
    """Fetch verified purchase receipt or invoice."""
    receipt = order_service.receipt_service.get_receipt(order_id)
    if not receipt:
        raise HTTPException(status_code=404, detail=f"Receipt for order '{order_id}' not found.")
    return receipt


@router.get("/{order_id}/audit")
async def get_order_audit_api(order_id: str):
    """Fetch chronological append-only audit events."""
    events = order_service.audit_logger.get_order_events(order_id)
    return {"order_id": order_id, "count": len(events), "events": [e.model_dump() for e in events]}
