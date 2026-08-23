"""FastAPI router for BOM generation, retrieval, validation, and human approval."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import (
    BillOfMaterials,
    BomItem,
    BomStatus,
    BOM,
    ComponentRequirement,
)
from backend.workline.procurement.service import procurement_service


router = APIRouter(prefix="/api/bom", tags=["Workline BOM Intelligence"])


class GenerateBOMRequest(BaseModel):
    project_id: str
    requirements: List[Dict[str, Any]]


class ApproveBOMRequest(BaseModel):
    approved_by: str = "Lead Engineer"
    comments: Optional[str] = None


class CreateBomRequest(BaseModel):
    bom_id: str
    project_id: str
    team_id: str = "default_team"
    source_decisions: Optional[List[str]] = None


class AddBomItemRequest(BaseModel):
    reference_designator: str
    part_number: str
    quantity: int = 1
    description: str = ""
    manufacturer: str = ""
    component_entity_id: str = ""


@router.post("", response_model=BillOfMaterials)
def create_bom_api(req: CreateBomRequest) -> BillOfMaterials:
    return procurement_service.create_bom(
        bom_id=req.bom_id,
        project_id=req.project_id,
        team_id=req.team_id,
        source_decisions=req.source_decisions,
    )


@router.get("", response_model=List[BillOfMaterials])
def list_boms_api(project_id: Optional[str] = None) -> List[BillOfMaterials]:
    return procurement_service.list_boms(project_id)


@router.post("/generate", response_model=BOM)
async def generate_bom_api(payload: GenerateBOMRequest):
    """Generate engineering BOM with landed cost optimization and SurrealDB persistence."""
    try:
        req_models = [ComponentRequirement.model_validate(r) for r in payload.requirements]
        bom, _ = await procurement_engine.generate_project_bom(payload.project_id, req_models)
        return bom
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"BOM generation failed: {str(exc)}")


@router.get("/{bom_id}", response_model=BOM)
async def get_bom_api(bom_id: str):
    """Fetch BOM by BOM ID or Project ID."""
    bom = await procurement_engine.get_bom(bom_id)
    if not bom:
        bom_p10 = procurement_service.get_bom(bom_id)
        if bom_p10:
            return bom_p10
        raise HTTPException(status_code=404, detail=f"BOM '{bom_id}' not found.")
    return bom


@router.post("/{bom_id}/items", response_model=BomItem)
def add_bom_item_api(bom_id: str, req: AddBomItemRequest) -> BomItem:
    try:
        return procurement_service.add_bom_item(
            bom_id=bom_id,
            reference_designator=req.reference_designator,
            part_number=req.part_number,
            quantity=req.quantity,
            description=req.description,
            manufacturer=req.manufacturer,
            component_entity_id=req.component_entity_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{bom_id}/validate")
def validate_bom_api(bom_id: str) -> Dict[str, Any]:
    try:
        status, issues = procurement_service.validate_bom(bom_id)
        return {"bom_id": bom_id, "status": status.value, "issues": issues}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{bom_id}/approve", response_model=BOM)
async def approve_bom_api(bom_id: str, payload: ApproveBOMRequest):
    """Human approval action transitioning BOM from READY_FOR_REVIEW to APPROVED."""
    bom = await procurement_engine.approve_bom(bom_id, approved_by=payload.approved_by)
    if not bom:
        raise HTTPException(status_code=404, detail=f"BOM '{bom_id}' not found.")
    return bom


# =========================================================================
# BOM x402 PAYMENT & REPORTING SHORTCUT ENDPOINTS
# =========================================================================

@router.post("/{bom_id}/payment/quote")
async def create_bom_quote_by_id_api(bom_id: str, payload: Optional[Dict[str, Any]] = None):
    """Issues frozen x402 payment quote for existing BOM."""
    from backend.workline.x402.bom_flow import bom_payment_flow
    bom = await procurement_engine.get_bom(bom_id)
    if not bom:
        bom = procurement_service.get_bom(bom_id)
        if not bom:
            raise HTTPException(status_code=404, detail=f"BOM '{bom_id}' not found.")

    items_list = [
        {
            "part_number": item.part_number,
            "description": item.description or "",
            "quantity": item.quantity,
            "unit_price_usd": getattr(item, "unit_price", 0.0),
            "manufacturer": getattr(item, "manufacturer", None),
            "supplier": getattr(item, "selected_supplier", getattr(item, "selected_vendor", "DigiKey")),
            "reference_designator": getattr(item, "reference_designator", ""),
        }
        for item in bom.items
    ]

    try:
        quote = bom_payment_flow.create_payment_quote(
            bom_data={"bom_id": bom.bom_id, "items": items_list},
            project_id=bom.project_id,
        )
        return {
            "status": "PAYMENT_REQUIRED",
            "quote": quote.model_dump(),
            "amount_usdc": quote.amount_usdc,
            "network": quote.network,
            "asset": quote.asset,
            "pay_to": quote.pay_to,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{bom_id}/payment/verify")
async def verify_bom_payment_by_id_api(bom_id: str, payload: Dict[str, Any]):
    """Verifies Algorand payment proof for a BOM payment."""
    from backend.workline.x402.bom_flow import bom_payment_flow
    quote_id = payload.get("quote_id") or payload.get("payment_request_id")
    if not quote_id:
        quote = bom_payment_flow.get_quote(bom_id)
        quote_id = quote.quote_id if quote else None

    if not quote_id:
        raise HTTPException(status_code=400, detail="Missing quote_id / payment_request_id.")

    ok, err, quote = await bom_payment_flow.settle_payment_proof(quote_id, payload)
    if not ok:
        raise HTTPException(status_code=400, detail=f"Payment verification failed: {err}")

    return {"status": "SETTLED", "quote": quote.model_dump() if quote else None}


@router.post("/{bom_id}/report")
async def generate_bom_report_by_id_api(bom_id: str, payload: Optional[Dict[str, Any]] = None):
    """Generates immutable PDF report for a settled BOM quote."""
    from backend.workline.x402.bom_flow import bom_payment_flow
    quote_id = (payload or {}).get("quote_id")
    if not quote_id:
        # Find settled quote for this BOM
        for q in bom_payment_flow._quotes.values():
            if q.bom_id == bom_id and q.status == "PAYMENT_SETTLED":
                quote_id = q.quote_id
                break

    if not quote_id:
        raise HTTPException(status_code=400, detail=f"No settled quote found for BOM '{bom_id}'.")

    ok, err, artifact = await bom_payment_flow.generate_payment_report(quote_id)
    if not ok or not artifact:
        raise HTTPException(status_code=400, detail=f"Report generation failed: {err}")

    return {
        "status": "REPORT_READY" if artifact.inr_available else "REPORT_READY_WITHOUT_INR",
        "artifact": artifact.model_dump(),
        "download_url": f"/api/x402/bom/report/{artifact.artifact_id}/download",
    }

