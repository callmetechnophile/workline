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
