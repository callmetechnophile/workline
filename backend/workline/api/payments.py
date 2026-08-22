"""FastAPI router for x402 payment authorization verification."""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workline.orders.models import Order, PaymentSession, PaymentStatus
from backend.workline.orders.service import order_service


router = APIRouter(prefix="/api/payments", tags=["Workline Payment Authorization (x402)"])


class VerifyPaymentRequest(BaseModel):
    order_id: str
    signed_proof: Dict[str, Any]


@router.get("/{payment_id}")
async def get_payment_status_api(payment_id: str):
    """Fetch status of a payment request / session."""
    session = order_service.session_manager.get_session(payment_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Payment session '{payment_id}' not found.")
    return session.model_dump()


@router.post("/{payment_id}/verify")
async def verify_payment_api(payment_id: str, payload: VerifyPaymentRequest):
    """
    Verify cryptographic payment proof and execute vendor order / manual checkout kit.
    """
    ok, order, receipt, err = await order_service.verify_payment_and_execute(
        order_id=payload.order_id,
        payment_id=payment_id,
        signed_proof=payload.signed_proof,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=f"Payment verification or execution failed: {err}")

    return {
        "status": "SUCCESS",
        "order": order.model_dump(),
        "receipt": receipt.model_dump() if receipt else None,
    }
