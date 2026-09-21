"""
FastAPI router for Contextual Comments.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query

from backend.workline.collaboration.comments.models import (
    ContextComment,
    CreateCommentRequest,
    UpdateCommentRequest,
)
from backend.workline.collaboration.comments.service import comment_service

router = APIRouter(prefix="/api/comments", tags=["Contextual Comments"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> str:
    """Extracts authenticated user ID from headers."""
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return "user_default_owner"


@router.post("", response_model=ContextComment)
def add_comment(
    payload: CreateCommentRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_name: Optional[str] = Header(None, alias="X-User-Name"),
):
    """Adds a contextual comment to a project or specific artifact."""
    author_id = get_current_user_id(x_user_id)
    return comment_service.add_comment(
        payload=payload,
        author_id=author_id,
        author_name=x_user_name or author_id,
    )


@router.get("", response_model=List[ContextComment])
def list_comments(
    project_id: str = Query(...),
    parent_type: Optional[str] = Query(None),
    parent_id: Optional[str] = Query(None),
):
    """Lists comments for a project, optionally filtered by parent artifact."""
    return comment_service.get_comments(
        project_id=project_id,
        parent_type=parent_type,
        parent_id=parent_id,
    )


@router.patch("/{comment_id}", response_model=ContextComment)
def update_comment(
    comment_id: str,
    payload: UpdateCommentRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Edits an existing comment."""
    actor_id = get_current_user_id(x_user_id)
    try:
        return comment_service.update_comment(comment_id, payload, actor_id)
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{comment_id}")
def delete_comment(
    comment_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    x_user_role: Optional[str] = Header(None, alias="X-User-Role"),
):
    """Deletes a comment."""
    actor_id = get_current_user_id(x_user_id)
    is_admin = x_user_role in ("OWNER", "ADMIN")
    try:
        success = comment_service.delete_comment(comment_id, actor_id, is_admin=is_admin)
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found.")
        return {"status": "DELETED", "comment_id": comment_id}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
