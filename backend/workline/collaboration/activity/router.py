"""
FastAPI router for Unified Activity Stream and Audit Trail.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query

from backend.workline.collaboration.activity.models import (
    ActorType,
    LogActivityRequest,
    UnifiedActivityEvent,
)
from backend.workline.collaboration.activity.service import activity_service

router = APIRouter(prefix="/api/activity", tags=["Activity & Audit"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> str:
    """Extracts authenticated user ID from headers."""
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return "user_default_owner"


@router.get("", response_model=List[UnifiedActivityEvent])
def list_activity_events(
    project_id: Optional[str] = Query(None),
    actor_type: Optional[ActorType] = Query(None),
    target_type: Optional[str] = Query(None),
    limit: int = Query(50),
):
    """Lists project activity stream events with actor differentiation."""
    return activity_service.list_events(
        project_id=project_id,
        actor_type=actor_type,
        target_type=target_type,
        limit=limit,
    )


@router.post("", response_model=UnifiedActivityEvent)
def record_activity_event(
    payload: LogActivityRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
):
    """Records an activity or audit event."""
    actor_id = payload.actor_id or get_current_user_id(x_user_id)
    actor_name = payload.actor_name or x_user_name or actor_id
    return activity_service.record_event(
        project_id=payload.project_id,
        team_id=payload.team_id,
        actor_type=payload.actor_type,
        actor_id=actor_id,
        actor_name=actor_name,
        event_type=payload.event_type,
        target_type=payload.target_type,
        target_id=payload.target_id,
        target_name=payload.target_name,
        summary=payload.summary,
        receipt_id=payload.receipt_id,
        metadata=payload.metadata,
    )
