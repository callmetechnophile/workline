"""
FastAPI endpoints for Requirements, Design Constraints, and Engineering Validation.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from backend.workline.validation.models import (
    ConstraintOperator,
    ConstraintSeverity,
    ConstraintStatus,
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
    RequirementOverviewSummary,
    RequirementPriority,
    RequirementStatus,
    ValidationResult,
)
from backend.workline.validation.service import validation_service

router = APIRouter(tags=["Engineering Validation & Requirements"])


# ==================== REQUEST SCHEMAS ====================

class CreateRequirementRequest(BaseModel):
    requirement_id: str
    project_id: str
    title: Optional[str] = None
    description: str
    category: RequirementCategory = RequirementCategory.ELECTRICAL
    parameter: Optional[str] = None
    target_value: Optional[str] = None
    unit: Optional[str] = None
    priority: RequirementPriority = RequirementPriority.HIGH
    status: RequirementStatus = RequirementStatus.ACTIVE
    verification_method: Optional[str] = "Simulation"
    source: Optional[str] = None
    constraints: List[EngineeringConstraint] = []
    team_id: str = "default_team"


class UpdateRequirementRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RequirementCategory] = None
    parameter: Optional[str] = None
    target_value: Optional[str] = None
    unit: Optional[str] = None
    priority: Optional[RequirementPriority] = None
    status: Optional[RequirementStatus] = None
    verification_method: Optional[str] = None
    source: Optional[str] = None


class CreateConstraintRequest(BaseModel):
    constraint_id: str
    property: str
    operator: ConstraintOperator = ConstraintOperator.LTE
    required_value: str
    required_unit: Optional[str] = None
    project_id: Optional[str] = None
    requirement_id: Optional[str] = None
    category: Optional[str] = "ELECTRICAL"
    severity: ConstraintSeverity = ConstraintSeverity.CRITICAL
    verification_method: Optional[str] = "Simulation"
    source: Optional[str] = None


class ValidateCandidateRequest(BaseModel):
    candidate_component_id: str


class CompareComponentsRequest(BaseModel):
    requirement_id: str
    candidate_ids: List[str]


# ==================== REQUIREMENT ENDPOINTS ====================

@router.post("/api/requirements", response_model=EngineeringRequirement)
def create_requirement_endpoint(req: CreateRequirementRequest) -> EngineeringRequirement:
    """Creates a new structured engineering requirement."""
    return validation_service.create_requirement(
        requirement_id=req.requirement_id,
        project_id=req.project_id,
        title=req.title,
        description=req.description,
        category=req.category,
        parameter=req.parameter,
        target_value=req.target_value,
        unit=req.unit,
        priority=req.priority,
        status=req.status,
        verification_method=req.verification_method,
        source=req.source,
        constraints=req.constraints,
        team_id=req.team_id,
    )


@router.get("/api/requirements", response_model=List[EngineeringRequirement])
def list_requirements_endpoint(project_id: Optional[str] = None) -> List[EngineeringRequirement]:
    """Lists requirements, optionally filtered by project_id."""
    return validation_service.list_requirements(project_id)


@router.get("/api/requirements/{requirement_id}", response_model=EngineeringRequirement)
def get_requirement_endpoint(requirement_id: str) -> EngineeringRequirement:
    """Fetches a single requirement by ID."""
    req = validation_service.get_requirement(requirement_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement '{requirement_id}' not found.")
    return req


@router.put("/api/requirements/{requirement_id}", response_model=EngineeringRequirement)
@router.patch("/api/requirements/{requirement_id}", response_model=EngineeringRequirement)
def update_requirement_endpoint(requirement_id: str, payload: UpdateRequirementRequest) -> EngineeringRequirement:
    """Updates an existing requirement."""
    updates = payload.model_dump(exclude_unset=True)
    updated = validation_service.update_requirement(requirement_id, updates)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement '{requirement_id}' not found.")
    return updated


@router.delete("/api/requirements/{requirement_id}")
def delete_requirement_endpoint(requirement_id: str) -> Dict[str, Any]:
    """Deletes a requirement and its associated constraints."""
    ok = validation_service.delete_requirement(requirement_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Requirement '{requirement_id}' not found.")
    return {"deleted": True, "requirement_id": requirement_id}


# ==================== CONSTRAINT ENDPOINTS ====================

@router.post("/api/constraints", response_model=EngineeringConstraint)
def create_constraint_endpoint(payload: CreateConstraintRequest) -> EngineeringConstraint:
    """Creates a new design constraint with optional requirement link."""
    return validation_service.create_constraint(
        constraint_id=payload.constraint_id,
        property_name=payload.property,
        operator=payload.operator,
        required_value=payload.required_value,
        project_id=payload.project_id,
        requirement_id=payload.requirement_id,
        required_unit=payload.required_unit,
        category=payload.category,
        severity=payload.severity,
        verification_method=payload.verification_method,
        source=payload.source,
    )


@router.get("/api/constraints", response_model=List[EngineeringConstraint])
def list_constraints_endpoint(
    project_id: Optional[str] = None,
    requirement_id: Optional[str] = None,
) -> List[EngineeringConstraint]:
    """Lists design constraints filtered by project or requirement."""
    return validation_service.list_constraints(project_id=project_id, requirement_id=requirement_id)


@router.delete("/api/constraints/{constraint_id}")
def delete_constraint_endpoint(constraint_id: str) -> Dict[str, Any]:
    """Deletes a design constraint."""
    ok = validation_service.delete_constraint(constraint_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Constraint '{constraint_id}' not found.")
    return {"deleted": True, "constraint_id": constraint_id}


# ==================== VALIDATION OVERVIEW & CANDIDATE MATCHING ====================

@router.get("/api/projects/{project_id}/validation/overview", response_model=RequirementOverviewSummary)
def get_project_validation_overview_endpoint(project_id: str) -> RequirementOverviewSummary:
    """Returns aggregated summary metrics of requirements, constraints, and validation results."""
    return validation_service.get_project_validation_overview(project_id)


@router.post("/api/requirements/{requirement_id}/validate", response_model=ValidationResult)
def validate_requirement_candidate_endpoint(
    requirement_id: str, req: ValidateCandidateRequest
) -> ValidationResult:
    """Evaluates a component candidate against a specific requirement."""
    try:
        return validation_service.validate_candidate(requirement_id, req.candidate_component_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/api/validations/{validation_id}", response_model=ValidationResult)
def get_validation_endpoint(validation_id: str) -> ValidationResult:
    """Retrieves a cached or stored validation result."""
    val = validation_service.get_validation(validation_id)
    if not val:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Validation result not found")
    return val


@router.post("/api/components/compare")
def compare_components_endpoint(req: CompareComponentsRequest) -> Dict[str, Any]:
    """Compares multiple candidate components against a target requirement."""
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


# ==================== PROJECT-SCOPED ALIASES ====================

@router.get("/api/projects/{project_id}/requirements", response_model=List[EngineeringRequirement])
def list_project_requirements_endpoint(project_id: str) -> List[EngineeringRequirement]:
    """Lists requirements scoped to a specific project."""
    return validation_service.list_requirements(project_id=project_id)


@router.post("/api/projects/{project_id}/requirements", response_model=EngineeringRequirement)
def create_project_requirement_endpoint(project_id: str, req: CreateRequirementRequest) -> EngineeringRequirement:
    """Creates a requirement scoped to a specific project."""
    return validation_service.create_requirement(
        requirement_id=req.requirement_id,
        project_id=project_id,
        title=req.title,
        description=req.description,
        category=req.category,
        parameter=req.parameter,
        target_value=req.target_value,
        unit=req.unit,
        priority=req.priority,
        status=req.status,
        verification_method=req.verification_method,
        source=req.source,
        constraints=req.constraints,
        team_id=req.team_id,
    )


@router.get("/api/projects/{project_id}/constraints", response_model=List[EngineeringConstraint])
def list_project_constraints_endpoint(project_id: str) -> List[EngineeringConstraint]:
    """Lists constraints scoped to a specific project."""
    return validation_service.list_constraints(project_id=project_id)


@router.post("/api/projects/{project_id}/constraints", response_model=EngineeringConstraint)
def create_project_constraint_endpoint(project_id: str, payload: CreateConstraintRequest) -> EngineeringConstraint:
    """Creates a constraint scoped to a specific project."""
    return validation_service.create_constraint(
        constraint_id=payload.constraint_id,
        property_name=payload.property,
        operator=payload.operator,
        required_value=payload.required_value,
        project_id=project_id,
        requirement_id=payload.requirement_id,
        required_unit=payload.required_unit,
        category=payload.category,
        severity=payload.severity,
        verification_method=payload.verification_method,
        source=payload.source,
    )


@router.get("/api/projects/{project_id}/validation", response_model=RequirementOverviewSummary)
def get_project_validation_endpoint(project_id: str) -> RequirementOverviewSummary:
    """Returns aggregated validation summary for a project."""
    return validation_service.get_project_validation_overview(project_id)

