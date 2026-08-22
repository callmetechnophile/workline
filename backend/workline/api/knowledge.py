"""FastAPI router for Engineering Knowledge and Decision Memory."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from backend.workline.knowledge import (
    Actor,
    ActorType,
    ConflictReport,
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
    RequirementCategory,
    RequirementStatus,
    RetrievedKnowledgeItem,
    TraceabilityChain,
    UnauthorizedApprovalError,
    knowledge_service,
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class ApproveBody(BaseModel):
    actor_id: str = "user"
    actor_type: str = "HUMAN"


class RejectBody(BaseModel):
    actor_id: str = "user"
    actor_type: str = "HUMAN"
    reason: Optional[str] = None


class SearchBody(BaseModel):
    project_id: str
    query: str
    object_types: Optional[List[str]] = None
    limit: int = 10


# ---------------------------------------------------------
# Decisions Endpoints
# ---------------------------------------------------------

@router.post("/decisions", response_model=EngineeringDecision)
def api_create_decision(payload: EngineeringDecision):
    try:
        return knowledge_service.create_decision(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/decisions", response_model=List[EngineeringDecision])
def api_list_decisions(
    project_id: str = Query(...),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    try:
        cat_enum = DecisionCategory[category.upper()] if category and category.upper() in DecisionCategory.__members__ else None
        stat_enum = DecisionStatus[status.upper()] if status and status.upper() in DecisionStatus.__members__ else None
        return knowledge_service.list_decisions(project_id, category=cat_enum, status=stat_enum)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decisions/{decision_id}", response_model=EngineeringDecision)
def api_get_decision(decision_id: str):
    dec = knowledge_service.get_decision(decision_id)
    if not dec:
        raise HTTPException(status_code=404, detail="Decision not found.")
    return dec


@router.post("/decisions/{decision_id}/approve", response_model=EngineeringDecision)
def api_approve_decision(decision_id: str, payload: ApproveBody):
    try:
        act_type = ActorType[payload.actor_type.upper()] if payload.actor_type.upper() in ActorType.__members__ else ActorType.HUMAN
        actor = Actor(actor_type=act_type, actor_id=payload.actor_id)
        return knowledge_service.approve_decision(decision_id, actor=actor)
    except UnauthorizedApprovalError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decisions/{decision_id}/reject", response_model=EngineeringDecision)
def api_reject_decision(decision_id: str, payload: RejectBody):
    try:
        act_type = ActorType[payload.actor_type.upper()] if payload.actor_type.upper() in ActorType.__members__ else ActorType.HUMAN
        actor = Actor(actor_type=act_type, actor_id=payload.actor_id)
        return knowledge_service.reject_decision(decision_id, actor=actor, reason=payload.reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/decisions/{decision_id}/supersede")
def api_supersede_decision(decision_id: str, payload: EngineeringDecision):
    try:
        old_dec, new_dec = knowledge_service.supersede_decision(decision_id, payload, actor=payload.created_by)
        return {"old_decision": old_dec, "new_decision": new_dec}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Requirements Endpoints
# ---------------------------------------------------------

@router.post("/requirements", response_model=EngineeringRequirement)
def api_create_requirement(payload: EngineeringRequirement):
    try:
        return knowledge_service.create_requirement(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/requirements", response_model=List[EngineeringRequirement])
def api_list_requirements(
    project_id: str = Query(...),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    try:
        cat_enum = RequirementCategory[category.upper()] if category and category.upper() in RequirementCategory.__members__ else None
        stat_enum = RequirementStatus[status.upper()] if status and status.upper() in RequirementStatus.__members__ else None
        return knowledge_service.list_requirements(project_id, category=cat_enum, status=stat_enum)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traceability/{requirement_id}", response_model=TraceabilityChain)
def api_get_traceability(requirement_id: str):
    try:
        return knowledge_service.get_requirement_traceability(requirement_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Findings & Lessons Endpoints
# ---------------------------------------------------------

@router.post("/findings", response_model=EngineeringFinding)
def api_create_finding(payload: EngineeringFinding):
    try:
        return knowledge_service.create_finding(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/findings", response_model=List[EngineeringFinding])
def api_list_findings(project_id: str = Query(...)):
    try:
        return knowledge_service.list_findings(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lessons", response_model=EngineeringLesson)
def api_create_lesson(payload: EngineeringLesson):
    try:
        return knowledge_service.create_lesson(payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lessons", response_model=List[EngineeringLesson])
def api_list_lessons(project_id: str = Query(...)):
    try:
        return knowledge_service.list_lessons(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------
# Search & Conflict Endpoints
# ---------------------------------------------------------

@router.post("/search", response_model=List[RetrievedKnowledgeItem])
def api_search_knowledge(payload: SearchBody):
    try:
        return knowledge_service.search_knowledge(
            project_id=payload.project_id,
            query=payload.query,
            object_types=payload.object_types,
            limit=payload.limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conflicts/{project_id}", response_model=ConflictReport)
def api_detect_conflicts(project_id: str):
    try:
        return knowledge_service.detect_conflicts(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
