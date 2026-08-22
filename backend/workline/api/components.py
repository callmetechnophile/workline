"""FastAPI router for canonical component inspection, vendor listings, and datasheet metadata."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException

from backend.workline.procurement.engine import procurement_engine


router = APIRouter(prefix="/api/components", tags=["Workline Components"])


@router.get("/{component_id}")
async def get_component_api(component_id: str):
    """Fetch canonical component candidate details."""
    cand = procurement_engine.get_component(component_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Component '{component_id}' not found in cache.")
    return cand.model_dump()


@router.get("/{component_id}/listings")
async def get_component_listings_api(component_id: str):
    """Fetch active vendor listings for a canonical component."""
    cand = procurement_engine.get_component(component_id)
    if not cand:
        raise HTTPException(status_code=404, detail=f"Component '{component_id}' not found.")
    return {"component_id": component_id, "listings": [l.model_dump() for l in cand.listings]}


@router.get("/{component_id}/datasheet")
async def get_component_datasheet_api(component_id: str):
    """Fetch verified datasheet metadata for a canonical component."""
    cand = procurement_engine.get_component(component_id)
    if not cand or not cand.datasheet:
        raise HTTPException(status_code=404, detail=f"Datasheet for component '{component_id}' not found.")
    return cand.datasheet.model_dump()
