"""FastAPI routes for Engineering Design Decisions."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from backend.workline.decision.models import (
    DecisionCandidate,
    DecisionCriterion,
    DecisionType,
    EngineeringDecision,
)
from backend.workline.decision.service import decision_service

router = APIRouter(tags=["Engineering Decisions"])


class CreateDecisionRequest(BaseModel):
    decision_id: str
    project_id: str
    title: str
    description: str
    decision_type: DecisionType = DecisionType.COMPONENT_SELECTION
    criteria: Optional[List[DecisionCriterion]] = None
    team_id: str = "default_team"
    created_by: str = "engineer"


class RecommendDecisionRequest(BaseModel):
    candidates: List[DecisionCandidate]
    raw_matrix: Dict[str, Dict[str, float]] = {}


class ApproveDecisionRequest(BaseModel):
    approved_by: str
    role: str = "ENGINEER"


class RejectDecisionRequest(BaseModel):
    rejected_by: str
    reason: str


@router.post("/api/decisions", response_model=EngineeringDecision)
def create_decision(req: CreateDecisionRequest) -> EngineeringDecision:
    return decision_service.create_decision(
        decision_id=req.decision_id,
        project_id=req.project_id,
        title=req.title,
        description=req.description,
        decision_type=req.decision_type,
        criteria=req.criteria,
        team_id=req.team_id,
        created_by=req.created_by,
    )


@router.get("/api/decisions", response_model=List[EngineeringDecision])
def list_decisions(project_id: Optional[str] = None) -> List[EngineeringDecision]:
    return decision_service.list_decisions(project_id)


@router.get("/api/decisions/{decision_id}", response_model=EngineeringDecision)
def get_decision(decision_id: str) -> EngineeringDecision:
    dec = decision_service.get_decision(decision_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found")
    return dec


@router.post("/api/decisions/{decision_id}/recommend", response_model=EngineeringDecision)
def recommend_decision(
    decision_id: str, req: RecommendDecisionRequest
) -> EngineeringDecision:
    try:
        return decision_service.generate_recommendation(
            decision_id, req.candidates, req.raw_matrix
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/decisions/{decision_id}/approve", response_model=EngineeringDecision)
def approve_decision(
    decision_id: str, req: ApproveDecisionRequest
) -> EngineeringDecision:
    try:
        return decision_service.approve_decision(decision_id, req.approved_by, req.role)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/api/decisions/{decision_id}/reject", response_model=EngineeringDecision)
def reject_decision(
    decision_id: str, req: RejectDecisionRequest
) -> EngineeringDecision:
    try:
        return decision_service.reject_decision(decision_id, req.rejected_by, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/decisions/{decision_id}/history", response_model=List[EngineeringDecision])
def get_decision_history(decision_id: str) -> List[EngineeringDecision]:
    return decision_service.get_history(decision_id)
