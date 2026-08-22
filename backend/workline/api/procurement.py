"""FastAPI router for procurement search, comparison, validation, and multi-vendor optimization."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.workline.procurement.engine import procurement_engine
from backend.workline.procurement.models import (
    ComponentCandidate,
    ComponentRequirement,
    DeterministicValidationReport,
    ProcurementPlan,
)


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


@router.post("/search")
async def search_components_api(payload: SearchRequest):
    """Search components across supported vendor sources (DigiKey, Mouser, Robu, Robocraze)."""
    try:
        candidates = await procurement_engine.search_engine.search_vendors(payload.query, limit_per_source=payload.limit)
        for c in candidates:
            procurement_engine._components[c.component_id] = c
        return {"query": payload.query, "count": len(candidates), "candidates": [c.model_dump() for c in candidates]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Component search failed: {str(exc)}")


@router.post("/validate", response_model=DeterministicValidationReport)
async def validate_component_api(payload: ValidateRequest):
    """Programmatically validate component specifications against engineering requirements."""
    try:
        cand = ComponentCandidate.model_validate(payload.candidate)
        req = ComponentRequirement.model_validate(payload.requirement)
        report = procurement_engine.validator.validate(cand, req)
        return report
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(exc)}")


@router.post("/compare")
async def compare_components_api(payload: CompareRequest):
    """Compare multiple components side-by-side across electrical, physical, interface, and vendor pricing dimensions."""
    try:
        results = []
        for cid in payload.component_ids:
            c = procurement_engine.get_component(cid)
            if c:
                results.append(c.model_dump())
            else:
                results.append({"component_id": cid, "status": "UNKNOWN"})
        return {"count": len(results), "components": results}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(exc)}")


@router.post("/optimize", response_model=ProcurementPlan)
async def optimize_procurement_api(payload: OptimizeRequest):
    """Generate multi-vendor optimization plan for a set of project requirements."""
    try:
        req_models = [ComponentRequirement.model_validate(r) for r in payload.requirements]
        _, plan = await procurement_engine.generate_project_bom(payload.project_id, req_models)
        return plan
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Procurement optimization failed: {str(exc)}")
