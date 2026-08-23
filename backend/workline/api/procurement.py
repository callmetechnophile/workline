"""FastAPI router for procurement search, comparison, validation, and multi-vendor optimization."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import (
    ComponentCandidate,
    ComponentRequirement,
    DeterministicValidationReport,
    ProcurementPackage,
    ProcurementPlan,
    SupplierOffer,
)
from backend.workline.procurement.service import procurement_service


router = APIRouter(prefix="/api/procurement", tags=["Workline Procurement"])


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


class ValidateRequest(BaseModel):
    candidate: Dict[str, Any]
    requirement: Dict[str, Any]


class CompareRequest(BaseModel):
    component_ids: List[str]


class OptimizeRequest(BaseModel):
    project_id: str
    requirements: List[Dict[str, Any]]


class GeneratePackageRequest(BaseModel):
    bom_id: str


@router.post("/search")
async def search_components_api(payload: SearchRequest):
    """Search components across supported vendor sources (DigiKey, Mouser, Robu, Robocraze)."""
    try:
        candidates = await procurement_engine.search_engine.search_vendors(payload.query, limit_per_source=payload.limit)
        for c in candidates:
            procurement_engine._components[c.component_id] = c
        return {"query": payload.query, "count": len(candidates), "candidates": [c.model_dump() for c in candidates]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(exc)}")


@router.post("/validate", response_model=DeterministicValidationReport)
async def validate_candidate_api(payload: ValidateRequest):
    """Deterministically check candidate specifications against a target requirement."""
    try:
        cand_model = ComponentCandidate.model_validate(payload.candidate)
        req_model = ComponentRequirement.model_validate(payload.requirement)
        report = procurement_engine.validator.validate(cand_model, req_model)
        return report
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Validation error: {str(exc)}")


@router.post("/compare")
async def compare_components_api(payload: CompareRequest):
    """Side-by-side parametric comparison for two or more component candidates."""
    try:
        result = procurement_engine.compare_components(payload.component_ids)
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Comparison failed: {str(exc)}")


@router.post("/optimize", response_model=ProcurementPlan)
async def optimize_procurement_api(payload: OptimizeRequest):
    """Generate multi-vendor sourcing options (lowest-cost vs consolidated vs fastest)."""
    try:
        req_models = [ComponentRequirement.model_validate(r) for r in payload.requirements]
        _, plan = await procurement_engine.generate_project_bom(payload.project_id, req_models)
        return plan
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(exc)}")


@router.get("/offers/{part_number}", response_model=List[SupplierOffer])
def get_supplier_offers_api(part_number: str) -> List[SupplierOffer]:
    """Retrieve supplier offers and price breaks for a component."""
    return procurement_service.get_offers(part_number)


@router.post("/package", response_model=ProcurementPackage)
def generate_procurement_package_api(req: GeneratePackageRequest) -> ProcurementPackage:
    """Generate procurement package for Phase 5 x402 handoff."""
    try:
        return procurement_service.generate_procurement_package(req.bom_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/quote")
async def create_procurement_quote_endpoint(payload: Dict[str, Any]):
    """
    R5 Quote Generation Capability:
    Creates an immutable, frozen x402 payment quote for a BOM.
    """
    from backend.workline.x402.bom_flow import bom_payment_flow
    project_id = payload.get("project_id", "default_project")
    bom_data = payload.get("bom", payload)
    try:
        quote = bom_payment_flow.create_payment_quote(
            bom_data=bom_data,
            project_id=project_id,
        )
        return {
            "quote_id": quote.quote_id,
            "payment_request_id": quote.payment_request_id,
            "bom_id": quote.bom_id,
            "project_id": quote.project_id,
            "amount_usd": quote.amount_usd,
            "amount_usdc": quote.amount_usdc,
            "asset_id": str(quote.asset_id),
            "asset": quote.asset,
            "network": quote.network,
            "pay_to": quote.pay_to,
            "expires_at": quote.expires_at,
            "status": quote.status.value if hasattr(quote.status, "value") else str(quote.status),
        }
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/quote/{quote_id}")
async def get_procurement_quote_endpoint(quote_id: str):
    """Retrieves real-time status of an immutable procurement quote."""
    from backend.workline.x402.bom_flow import bom_payment_flow
    quote = bom_payment_flow.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote '{quote_id}' not found.")
    return quote.model_dump()


@router.post("/{quote_id}/pay")
async def pay_procurement_quote_endpoint(quote_id: str, payload: Dict[str, Any]):
    """
    R5 x402 Payment Settlement Endpoint:
    Receives Pera Wallet signed proof and settles against GoPlausible facilitator.
    If payment proof is absent, returns HTTP 402 with x402 requirements.
    """
    from backend.workline.x402.bom_flow import bom_payment_flow
    quote = bom_payment_flow.get_quote(quote_id)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Quote '{quote_id}' not found.")

    tx_hash = payload.get("tx_hash") or payload.get("transaction_id") or payload.get("signature")
    if not tx_hash:
        # Return HTTP 402 Payment Required
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "status_code": 402,
                "quote_id": quote.quote_id,
                "payment_request_id": quote.payment_request_id,
                "amount_usdc": quote.amount_usdc,
                "amount_usd": quote.amount_usd,
                "asset": quote.asset,
                "asset_id": quote.asset_id,
                "network": quote.network,
                "pay_to": quote.pay_to,
                "expires_at": quote.expires_at,
                "facilitator": quote.facilitator,
            },
            headers={
                "X-Payment-Required": (
                    f"x402 network={quote.network} asset={quote.asset} asset_id={quote.asset_id} "
                    f"amount={quote.amount_usdc:.2f} pay_to={quote.pay_to} quote_id={quote.quote_id}"
                )
            },
        )

    ok, err, settled_quote = await bom_payment_flow.settle_payment_proof(
        quote_id=quote_id,
        proof_data=payload,
    )
    if not ok:
        raise HTTPException(status_code=400, detail=f"Settlement verification failed: {err}")

    return {
        "status": "SETTLED",
        "quote_id": settled_quote.quote_id,
        "payment_request_id": settled_quote.payment_request_id,
        "amount_usdc": settled_quote.amount_usdc,
        "transaction_id": settled_quote.transaction_id,
        "settled_at": settled_quote.settled_at,
        "quote": settled_quote.model_dump(),
    }
