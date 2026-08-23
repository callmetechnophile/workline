"""
Workline R5 - Procurement, Multi-Vendor Sourcing, Orders & x402 Payment Service
Production Entrypoint for Internal Render Worker Container
"""

import os
import secrets
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, Security, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field
from loguru import logger

# Import Procurement, Orders, Payments, and BOM Modules
from backend.workline.api.bom import router as bom_router
from backend.workline.api.procurement import router as procurement_router
from backend.workline.api.orders import router as orders_router
from backend.workline.api.payments import router as payments_router
from backend.workline.x402 import x402_router
from backend.workline.procurement.engine import procurement_engine
from backend.workline.orders.service import order_service
from backend.workline.orders.models import Order, OrderPlan, PaymentRequest, PaymentStatus

SERVICE_NAME = "workline-r5"
SERVICE_VERSION = "1.0.0-rc1"

# Service-to-service internal authentication token (injected via environment by Render)
R5_SERVICE_TOKEN = os.getenv("R5_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))

bearer_scheme = HTTPBearer(auto_error=False)


async def verify_internal_service_auth(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme)
) -> bool:
    """
    Validates internal service-to-service authorization token from R1 Core Gateway.
    Supports Authorization: Bearer <token> and X-Workline-Service-Token headers.
    Uses constant-time comparison to prevent timing attacks.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials
    elif "X-Workline-Service-Token" in request.headers:
        token = request.headers["X-Workline-Service-Token"]

    if not R5_SERVICE_TOKEN:
        # Development fallback if token is unset
        return True

    if not token or not secrets.compare_digest(token, R5_SERVICE_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: Invalid or missing internal service authorization token",
        )

    return True


app = FastAPI(
    title="Workline R5 - Procurement & x402 Payment Service",
    description="Internal microservice for component intelligence, multi-vendor sourcing, orders, and cryptographic x402 payment authorization.",
    version=SERVICE_VERSION,
    docs_url="/docs" if os.getenv("WORKLINE_ENV") != "production" else None,
    redoc_url=None,
)

# CORS Policy: Restricted strictly to internal cluster communications.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:10000", "http://127.0.0.1:10000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
@app.get("/health", tags=["Health"])
@app.get("/version", tags=["Health"])
@app.get("/service", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Lightweight health probe endpoint for Render uptime monitoring.
    Never executes live vendor orders, paid transactions, or remote scraping.
    """
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


# Request & Response Schemas for Internal Procurement APIs
class InternalSearchRequest(BaseModel):
    query: str
    limit: int = 10


class InternalQuoteRequest(BaseModel):
    bom_id: str


class InternalCreateOrderPlanRequest(BaseModel):
    project_id: str
    bom_id: str
    user_id: Optional[str] = "user:engineer"
    team_id: Optional[str] = "team:default"


class InternalCreateOrdersRequest(BaseModel):
    plan_id: str
    user_id: Optional[str] = "user:engineer"
    team_id: Optional[str] = "team:default"
    user_role: Optional[str] = "ENGINEER"


class InternalPaymentRequest(BaseModel):
    order_id: str


class InternalVerifyPaymentRequest(BaseModel):
    order_id: str
    payment_id: str
    signed_proof: Dict[str, Any]


@app.post("/internal/procurement/search", tags=["Internal"])
async def internal_procurement_search(
    payload: InternalSearchRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Searches components across supported vendor sources."""
    try:
        candidates = await procurement_engine.search_engine.search_vendors(payload.query, limit_per_source=payload.limit)
        for c in candidates:
            procurement_engine._components[c.component_id] = c
        return {
            "query": payload.query,
            "count": len(candidates),
            "candidates": [c.model_dump() for c in candidates]
        }
    except Exception as e:
        logger.error(f"Procurement search failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Search failed: {str(e)}")


@app.post("/internal/procurement/quote", tags=["Internal"])
async def internal_procurement_quote(
    payload: InternalQuoteRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Generates an optimized multi-vendor procurement quote package."""
    try:
        package = await procurement_engine.generate_procurement_package(payload.bom_id)
        return package.model_dump()
    except Exception as e:
        logger.error(f"Quote generation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Quote generation failed: {str(e)}")


@app.post("/internal/procurement/orders/plan", tags=["Internal"])
async def internal_create_order_plan(
    payload: InternalCreateOrderPlanRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Generates an itemized OrderPlan from a BOM."""
    try:
        plan = await order_service.create_order_plan(payload.project_id, payload.bom_id)
        return plan.model_dump()
    except Exception as e:
        logger.error(f"Order plan creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order plan failed: {str(e)}")


@app.post("/internal/procurement/orders/create", tags=["Internal"])
async def internal_create_orders(
    payload: InternalCreateOrdersRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> List[Dict[str, Any]]:
    """Creates Order records and advances state machine."""
    try:
        orders = await order_service.create_orders_from_plan(
            plan_id=payload.plan_id,
            user_id=payload.user_id,
            team_id=payload.team_id,
            user_role=payload.user_role,
        )
        return [o.model_dump() for o in orders]
    except Exception as e:
        logger.error(f"Order creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Order creation failed: {str(e)}")


@app.post("/internal/procurement/payments/request", tags=["Internal"])
async def internal_request_payment(
    payload: InternalPaymentRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Generates an x402 HTTP 402 non-custodial cryptographic payment challenge."""
    try:
        order = order_service._orders.get(payload.order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{payload.order_id}' not found")
        payment_req = await order_service.payment_provider.create_payment_request(order)
        return payment_req.model_dump()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment request creation failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment request failed: {str(e)}")


@app.post("/internal/procurement/payments/verify", tags=["Internal"])
async def internal_verify_payment(
    payload: InternalVerifyPaymentRequest,
    _authenticated: bool = Depends(verify_internal_service_auth),
) -> Dict[str, Any]:
    """Verifies cryptographic payment proof and executes order."""
    try:
        ok, order, receipt, err = await order_service.verify_payment_and_execute(
            order_id=payload.order_id,
            payment_id=payload.payment_id,
            signed_proof=payload.signed_proof,
        )
        if not ok:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment verification failed: {err}")
        return {
            "status": "SUCCESS",
            "order": order.model_dump() if order else None,
            "receipt": receipt.model_dump() if receipt else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Payment verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Payment execution failed: {str(e)}")


# Mount Standard Procurement & Order Routers
app.include_router(bom_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(procurement_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(orders_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(payments_router, dependencies=[Depends(verify_internal_service_auth)])
app.include_router(x402_router, dependencies=[Depends(verify_internal_service_auth)])


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "10005"))
    uvicorn.run("backend.r5.main:app", host="0.0.0.0", port=port, reload=False)
