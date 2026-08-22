"""FastAPI router for BOM generation, retrieval, and human approval."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import BOM, ComponentRequirement


router = APIRouter(prefix="/api/bom", tags=["Workline BOM Intelligence"])


class GenerateBOMRequest(BaseModel):
    project_id: str
    requirements: List[Dict[str, Any]]


class ApproveBOMRequest(BaseModel):
    approved_by: str = "Lead Engineer"
    comments: Optional[str] = None


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
        raise HTTPException(status_code=404, detail=f"BOM '{bom_id}' not found.")
    return bom


@router.post("/{bom_id}/approve", response_model=BOM)
async def approve_bom_api(bom_id: str, payload: ApproveBOMRequest):
    """Human approval action transitioning BOM from READY_FOR_REVIEW to APPROVED."""
    bom = await procurement_engine.approve_bom(bom_id, approved_by=payload.approved_by)
    if not bom:
        raise HTTPException(status_code=404, detail=f"BOM '{bom_id}' not found.")
    return bom
