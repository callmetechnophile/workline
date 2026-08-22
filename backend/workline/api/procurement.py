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
