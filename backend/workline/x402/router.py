"""
FastAPI Router for Workline x402 Service Monetization Endpoints.
Handles 402 challenges, GoPlausible/Algorand payment verification, and service execution.
"""

from datetime import datetime, timedelta, timezone
import json
import os
import uuid
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Request, Response, status
from fastapi.responses import FileResponse
from loguru import logger

from backend.workline.x402.bom_flow import bom_payment_flow
from backend.workline.x402.catalog import service_catalog
from backend.workline.x402.config import x402_config
from backend.workline.x402.models import (
    PaymentProof,
    PaymentRecord,
    PaymentStatus,
    ServiceExecutionRequest,
    ServiceExecutionResponse,
    X402Challenge,
)
from backend.workline.x402.storage import x402_storage
from backend.workline.x402.verifier import x402_verifier

router = APIRouter(prefix="/api/x402", tags=["Workline x402 Service Monetization"])


# Helper function to generate 402 challenge response
def create_402_challenge_response(
    service_id: str,
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> Response:
    """Creates a structured HTTP 402 Payment Required response."""
    service = service_catalog.get_service(service_id)
    if not service or not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_id}' is not available or currently disabled.",
        )

    req_id = f"pay_req_{uuid.uuid4().hex[:12]}"
    nonce = uuid.uuid4().hex
    now = datetime.now(timezone.utc)
    expires = (now + timedelta(minutes=x402_config.challenge_ttl_minutes)).isoformat()

    challenge = X402Challenge(
        scheme="x402",
        network=service.network,
        asset=service.asset,
        asset_id=service.asset_id,
        amount=service.price_usdc,
        currency="USD",
        pay_to=x402_config.pay_to,
        nonce=nonce,
        payment_request_id=req_id,
        expires_at=expires,
        facilitator=x402_config.facilitator_url,
        service_id=service_id,
    )

    record = PaymentRecord(
        id=f"pay_rec_{uuid.uuid4().hex[:12]}",
        payment_request_id=req_id,
        service_id=service_id,
        user_id=user_id,
        project_id=project_id,
        amount=service.price_usdc,
        asset=service.asset,
        asset_id=service.asset_id,
        network=service.network,
        pay_to=x402_config.pay_to,
        facilitator=x402_config.facilitator_url,
        status=PaymentStatus.PAYMENT_REQUIRED,
        idempotency_key=idempotency_key,
        expires_at=expires,
    )
    x402_storage.save_record(record)

    logger.info(
        f"[x402] Issued 402 Challenge '{req_id}' for service '{service_id}' (${service.price_usdc} {service.asset})"
    )

    headers = {
        "X-Payment-Required": (
            f"x402 network={service.network} asset={service.asset} asset_id={service.asset_id} "
            f"amount={service.price_usdc:.2f} pay_to={x402_config.pay_to} payment_request_id={req_id}"
        )
    }

    body = {
        "error": "Payment Required",
        "status_code": 402,
        "message": f"Payment of {service.price_usdc:.2f} {service.asset} on {service.network} required to execute '{service.name}'.",
        "service_id": service_id,
        "service_name": service.name,
        "challenge": challenge.model_dump(),
    }

    return Response(
        content=json.dumps(body),
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        media_type="application/json",
        headers=headers,
    )


# Helper function to extract payment proof from headers or request payload
def extract_payment_proof(
    request: Request,
    payload: Dict[str, Any],
) -> Optional[PaymentProof]:
    """Extracts PaymentProof from X-PAYMENT header, Authorization, or JSON payload."""
    # 1. Header: X-PAYMENT or X-Payment
    raw_header = request.headers.get("X-PAYMENT") or request.headers.get("X-Payment")
    if raw_header:
        try:
            parsed = json.loads(raw_header)
            return PaymentProof(**parsed)
        except Exception:
            # Handle token/hash format in header
            if "pay_req_" in raw_header:
                parts = raw_header.split(":")
                return PaymentProof(
                    payment_request_id=parts[0].strip(),
                    tx_hash=parts[1].strip() if len(parts) > 1 else None,
                )

    # 2. Body proof field
    if "payment_proof" in payload:
        try:
            return PaymentProof(**payload["payment_proof"])
        except Exception:
            pass

    if "payment_request_id" in payload:
        return PaymentProof(
            payment_request_id=payload["payment_request_id"],
            tx_hash=payload.get("tx_hash") or payload.get("signature"),
            payer_address=payload.get("payer_address"),
        )

    return None


async def handle_service_execution_flow(
    service_id: str,
    payload: Dict[str, Any],
    request: Request,
    idempotency_key: Optional[str] = None,
) -> Response:
    """Core 402 monetization handler for all Workline services."""
    service = service_catalog.get_service(service_id)
    if not service or not service.enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_id}' is not available.",
        )

    # Idempotency check: Return existing result if this key was already processed successfully
    if idempotency_key:
        existing_rec = x402_storage.get_by_idempotency_key(idempotency_key)
        if existing_rec and existing_rec.status == PaymentStatus.EXECUTED and existing_rec.result_reference:
            logger.info(f"[x402] Idempotent hit for key '{idempotency_key}' (service '{service_id}')")
            return Response(
                content=json.dumps({
                    "status": "SUCCESS",
                    "service_id": service_id,
                    "idempotent": True,
                    "payment": {
                        "payment_id": existing_rec.payment_request_id,
                        "status": existing_rec.status.value,
                        "amount_usdc": existing_rec.amount,
                        "network": existing_rec.network,
                        "tx_hash": existing_rec.transaction_id,
                    },
                    "result": existing_rec.result_reference,
                }),
                status_code=status.HTTP_200_OK,
                media_type="application/json",
            )

    proof = extract_payment_proof(request, payload)

    # If no proof submitted, return 402 challenge immediately
    if not proof:
        return create_402_challenge_response(
            service_id=service_id,
            user_id=payload.get("user_id"),
            project_id=payload.get("project_id"),
            idempotency_key=idempotency_key,
        )

    # Find the active record for this payment_request_id
    record = x402_storage.get_record(proof.payment_request_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment request '{proof.payment_request_id}' not found or expired.",
        )

    # Verify payment through GoPlausible / Algorand verifier
    ok, err, record = await x402_verifier.verify_proof(record, proof)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment verification failed: {err}",
        )

    # Payment verified -> Execute the Workline service
    logger.info(f"[x402] Executing Workline service '{service_id}' for project '{payload.get('project_id')}'")
    service_result = await service_catalog.execute_service(service_id, payload)

    # Record execution completion
    now = datetime.now(timezone.utc)
    record.status = PaymentStatus.EXECUTED
    record.executed_at = now.isoformat()
    record.result_reference = service_result
    x402_storage.save_record(record)

    response_payload = {
        "status": "SUCCESS",
        "service_id": service_id,
        "payment": {
            "payment_id": record.payment_request_id,
            "status": record.status.value,
            "amount_usdc": record.amount,
            "asset": record.asset,
            "network": record.network,
            "tx_hash": record.transaction_id,
            "settled_at": record.settled_at,
        },
        "result": service_result,
        "executed_at": record.executed_at,
    }

    return Response(
        content=json.dumps(response_payload),
        status_code=status.HTTP_200_OK,
        media_type="application/json",
    )


# =========================================================================
# PUBLIC SERVICE DISCOVERY & PAYMENT STATUS
# =========================================================================

@router.get("/services")
async def list_available_services():
    """Returns public catalog of payable Workline AI services and Algorand pricing."""
    services = service_catalog.list_services()
    return {
        "network": x402_config.network,
        "asset": x402_config.asset,
        "asset_id": x402_config.asset_id,
        "pay_to": x402_config.pay_to,
        "facilitator_url": x402_config.facilitator_url,
        "enabled": x402_config.enabled,
        "service_count": len(services),
        "services": [s.model_dump() for s in services],
    }


@router.get("/services/{service_id}")
async def get_service_details(service_id: str):
    """Returns details for a specific payable service."""
    service = service_catalog.get_service(service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_id}' not found.",
        )
    return service.model_dump()


@router.get("/payments")
async def list_payments(
    user_id: Optional[str] = None,
    project_id: Optional[str] = None,
    limit: int = 50,
):
    """Lists audit history of x402 payment records."""
    records = x402_storage.list_records(user_id=user_id, project_id=project_id, limit=limit)
    return {
        "count": len(records),
        "payments": [r.model_dump() for r in records],
    }


@router.get("/payments/{payment_id}")
async def get_payment_status(payment_id: str):
    """Fetches real-time status of a payment challenge/record."""
    record = x402_storage.get_record(payment_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Payment record '{payment_id}' not found.",
        )
    return record.model_dump()


# =========================================================================
# SERVICE-SPECIFIC MONETIZATION ENDPOINTS
# =========================================================================

@router.post("/services/{service_id}/execute")
async def execute_service_generic(
    service_id: str,
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Generic endpoint to execute any payable service by ID."""
    return await handle_service_execution_flow(
        service_id=service_id,
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


@router.post("/bom/optimize")
async def execute_bom_optimize(
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Payable Service: BOM Sourcing Optimizer (0.50 USDC)."""
    return await handle_service_execution_flow(
        service_id="bom.optimize",
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


@router.post("/component/analyze")
async def execute_component_analyze(
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Payable Service: Component & Datasheet AI (0.25 USDC)."""
    return await handle_service_execution_flow(
        service_id="component.analyze",
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


@router.post("/research/engineering")
async def execute_research_engineering(
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Payable Service: Hardware Research Synthesis (1.00 USDC)."""
    return await handle_service_execution_flow(
        service_id="research.engineering",
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


@router.post("/simulation/thermal")
async def execute_simulation_thermal(
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Payable Service: Multi-Physics Thermal PINN (0.75 USDC)."""
    return await handle_service_execution_flow(
        service_id="simulation.thermal",
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


@router.post("/procurement/quote")
async def execute_procurement_quote(
    payload: Dict[str, Any],
    request: Request,
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    """Payable Service: Multi-Vendor RFQ Consolidation (0.25 USDC)."""
    return await handle_service_execution_flow(
        service_id="procurement.quote",
        payload=payload,
        request=request,
        idempotency_key=x_idempotency_key or payload.get("idempotency_key"),
    )


# =========================================================================
# AUTHORITATIVE BOM PROCUREMENT PAYMENT & REPORTING FLOW
# =========================================================================

@router.post("/bom/quote")
async def create_bom_payment_quote_api(payload: Dict[str, Any]):
    """
    Creates a frozen, authoritative payment quote for a BOM.
    Enforces strict parity: BOM Total USD == x402 Amount USDC on Algorand.
    """
    project_id = payload.get("project_id", "default_project")
    bom_data = payload.get("bom", payload)
    try:
        quote = bom_payment_flow.create_payment_quote(
            bom_data=bom_data,
            project_id=project_id,
        )
        return {
            "status": "PAYMENT_REQUIRED",
            "quote": quote.model_dump(),
            "challenge": {
                "scheme": "x402",
                "network": quote.network,
                "asset": quote.asset,
                "asset_id": quote.asset_id,
                "amount": quote.amount_usdc,
                "currency": "USD",
                "pay_to": quote.pay_to,
                "payment_request_id": quote.payment_request_id,
                "quote_id": quote.quote_id,
                "expires_at": quote.expires_at,
                "facilitator": quote.facilitator,
            },
        }
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error(f"[API] Error creating BOM payment quote: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get("/bom/quote/{quote_id}")
async def get_bom_payment_quote_api(quote_id: str):
    """Retrieves real-time status of a BOM payment quote."""
    quote = bom_payment_flow.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Quote '{quote_id}' not found.")
    return quote.model_dump()


@router.post("/bom/verify")
async def verify_and_settle_bom_payment_api(payload: Dict[str, Any]):
    """
    Submits Algorand payment proof and settles the frozen BOM quote.
    """
    quote_id = payload.get("quote_id") or payload.get("payment_request_id")
    if not quote_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quote_id or payment_request_id is required.")

    ok, err, quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote_id,
        proof_data=payload,
    )
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment verification failed: {err}")

    return {
        "status": "SETTLED",
        "quote_id": quote.quote_id,
        "payment_request_id": quote.payment_request_id,
        "amount_usdc": quote.amount_usdc,
        "transaction_id": quote.transaction_id,
        "settled_at": quote.settled_at,
        "quote": quote.model_dump(),
    }


@router.post("/bom/report")
async def generate_bom_payment_report_api(payload: Dict[str, Any]):
    """
    Compiles an auditable PDF payment report for a settled BOM quote.
    Queries CoinGecko ONCE for informational INR rate (resilient to failure).
    """
    quote_id = payload.get("quote_id") or payload.get("payment_request_id")
    if not quote_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="quote_id is required.")

    ok, err, artifact = await bom_payment_flow.generate_payment_report(quote_id=quote_id)
    if not ok or not artifact:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Report generation failed: {err}")

    return {
        "status": "REPORT_READY" if artifact.inr_available else "REPORT_READY_WITHOUT_INR",
        "artifact": artifact.model_dump(),
        "download_url": f"/api/x402/bom/report/{artifact.artifact_id}/download",
    }


@router.get("/bom/report/{artifact_id}")
async def get_bom_payment_report_metadata_api(artifact_id: str):
    """Fetches metadata for a compiled PDF payment report."""
    artifact = bom_payment_flow.get_report(artifact_id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Report artifact '{artifact_id}' not found.")
    return artifact.model_dump()


@router.get("/bom/report/{artifact_id}/download")
async def download_bom_payment_report_api(artifact_id: str):
    """Downloads the compiled PDF payment report artifact."""
    artifact = bom_payment_flow.get_report(artifact_id)
    if not artifact or not os.path.exists(artifact.filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report file not found on server.")

    return FileResponse(
        path=artifact.filepath,
        filename=artifact.filename,
        media_type="application/pdf",
    )

