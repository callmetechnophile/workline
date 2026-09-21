"""
FastAPI router for Sensitive Engineering Approvals.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query

from backend.workline.collaboration.approvals.models import (
    ApprovalRequest,
    ApprovalStatus,
    CreateApprovalRequest,
    ResolveApprovalRequest,
)
from backend.workline.collaboration.approvals.service import approval_service

router = APIRouter(prefix="/api/approvals", tags=["Engineering Approvals"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> str:
    """Extracts authenticated user ID from headers."""
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return "user_default_owner"


@router.post("", response_model=ApprovalRequest)
def create_approval_request(
    payload: CreateApprovalRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
):
    """Submits a sensitive action for approval."""
    actor_id = get_current_user_id(x_user_id)
    return approval_service.create_request(
        payload=payload,
        requester_id=actor_id,
        requester_name=x_user_name or actor_id,
    )


@router.get("", response_model=List[ApprovalRequest])
def list_approval_requests(
    project_id: Optional[str] = Query(None),
    status: Optional[ApprovalStatus] = Query(None),
    artifact_type: Optional[str] = Query(None),
):
    """Lists approval requests with optional status or artifact filters."""
    return approval_service.list_requests(
        project_id=project_id,
        status=status,
        artifact_type=artifact_type,
    )


@router.get("/{approval_id}", response_model=ApprovalRequest)
def get_approval_request(approval_id: str):
    """Gets details for an approval request."""
    req = approval_service.get_request(approval_id)
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    return req


@router.post("/{approval_id}/resolve", response_model=ApprovalRequest)
def resolve_approval_request(
    approval_id: str,
    payload: ResolveApprovalRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
):
    """Approves or rejects an engineering approval request."""
    actor_id = get_current_user_id(x_user_id)
    try:
        return approval_service.resolve_request(
            approval_id=approval_id,
            payload=payload,
            approver_id=actor_id,
            approver_name=x_user_name or actor_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
