"""FastAPI routes for BOM and Procurement Intelligence."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.workline.procurement.models import (
    BillOfMaterials,
    BomItem,
    BomStatus,
    ProcurementPackage,
    SupplierOffer,
)
from backend.workline.procurement.service import procurement_service

router = APIRouter(tags=["BOM and Procurement"])


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


class GeneratePackageRequest(BaseModel):
    bom_id: str


@router.post("/api/bom", response_model=BillOfMaterials)
def create_bom(req: CreateBomRequest) -> BillOfMaterials:
    return procurement_service.create_bom(
        bom_id=req.bom_id,
        project_id=req.project_id,
        team_id=req.team_id,
        source_decisions=req.source_decisions,
    )


@router.get("/api/bom", response_model=List[BillOfMaterials])
def list_boms(project_id: Optional[str] = None) -> List[BillOfMaterials]:
    return procurement_service.list_boms(project_id)


@router.get("/api/bom/{bom_id}", response_model=BillOfMaterials)
def get_bom(bom_id: str) -> BillOfMaterials:
    bom = procurement_service.get_bom(bom_id)
    if not bom:
        raise HTTPException(status_code=404, detail="BOM not found")
    return bom


@router.post("/api/bom/{bom_id}/items", response_model=BomItem)
def add_bom_item(bom_id: str, req: AddBomItemRequest) -> BomItem:
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


@router.post("/api/bom/{bom_id}/validate")
def validate_bom(bom_id: str) -> Dict[str, Any]:
    try:
        status, issues = procurement_service.validate_bom(bom_id)
        return {"bom_id": bom_id, "status": status.value, "issues": issues}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/procurement/offers/{part_number}", response_model=List[SupplierOffer])
def get_supplier_offers(part_number: str) -> List[SupplierOffer]:
    return procurement_service.get_offers(part_number)


@router.post("/api/procurement/package", response_model=ProcurementPackage)
def generate_procurement_package(req: GeneratePackageRequest) -> ProcurementPackage:
    try:
        return procurement_service.generate_procurement_package(req.bom_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
