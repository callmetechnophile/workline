"""FastAPI endpoints for Requirements and Engineering Validation."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.workline.validation.models import (
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
    ValidationResult,
)
from backend.workline.validation.service import validation_service

router = APIRouter(tags=["Engineering Validation"])


class CreateRequirementRequest(BaseModel):
    requirement_id: str
    project_id: str
    description: str
    category: RequirementCategory = RequirementCategory.ELECTRICAL
    constraints: List[EngineeringConstraint] = []
    priority: str = "HIGH"
    team_id: str = "default_team"


class ValidateCandidateRequest(BaseModel):
    candidate_component_id: str


class CompareComponentsRequest(BaseModel):
    requirement_id: str
    candidate_ids: List[str]


@router.post("/api/requirements", response_model=EngineeringRequirement)
def create_requirement(req: CreateRequirementRequest) -> EngineeringRequirement:
    return validation_service.create_requirement(
        requirement_id=req.requirement_id,
        project_id=req.project_id,
        description=req.description,
        category=req.category,
        constraints=req.constraints,
        priority=req.priority,
        team_id=req.team_id,
    )


@router.get("/api/requirements", response_model=List[EngineeringRequirement])
def list_requirements(project_id: Optional[str] = None) -> List[EngineeringRequirement]:
    return validation_service.list_requirements(project_id)


@router.get("/api/requirements/{requirement_id}", response_model=EngineeringRequirement)
def get_requirement(requirement_id: str) -> EngineeringRequirement:
    req = validation_service.get_requirement(requirement_id)
    if not req:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return req


@router.post("/api/requirements/{requirement_id}/validate", response_model=ValidationResult)
def validate_requirement_candidate(
    requirement_id: str, req: ValidateCandidateRequest
) -> ValidationResult:
    try:
        return validation_service.validate_candidate(requirement_id, req.candidate_component_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/validations/{validation_id}", response_model=ValidationResult)
def get_validation(validation_id: str) -> ValidationResult:
    val = validation_service.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=404, detail="Validation result not found")
    return val


@router.post("/api/components/compare")
def compare_components(req: CompareComponentsRequest) -> Dict[str, Any]:
    results = []
    for cid in req.candidate_ids:
        try:
            val = validation_service.validate_candidate(req.requirement_id, cid)
            results.append(val.model_dump())
        except ValueError:
            pass
    return {
        "requirement_id": req.requirement_id,
        "comparisons": results,
    }
