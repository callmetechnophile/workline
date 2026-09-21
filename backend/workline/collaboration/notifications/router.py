"""
FastAPI router for Centralized Notifications.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query

from backend.workline.collaboration.notifications.models import (
    CreateNotificationRequest,
    Notification,
)
from backend.workline.collaboration.notifications.service import notification_service

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> str:
    """Extracts authenticated user ID from headers."""
    if x_user_id and x_user_id.strip():
        return x_user_id.strip()
    return "user_default_owner"


@router.get("", response_model=Dict[str, Any])
def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50),
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Lists notifications and unread count for the authenticated user."""
    recipient_id = get_current_user_id(x_user_id)
    items = notification_service.list_notifications(
        recipient_id=recipient_id,
        unread_only=unread_only,
        limit=limit,
    )
    unread_count = notification_service.get_unread_count(recipient_id)
    return {
        "notifications": [n.model_dump() for n in items],
        "unread_count": unread_count,
    }


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Marks a single notification as read."""
    recipient_id = get_current_user_id(x_user_id)
    success = notification_service.mark_read(notification_id, recipient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"status": "READ", "notification_id": notification_id}


@router.post("/mark-all-read")
def mark_all_notifications_read(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Marks all notifications as read for current user."""
    recipient_id = get_current_user_id(x_user_id)
    count = notification_service.mark_all_read(recipient_id)
    return {"status": "SUCCESS", "marked_count": count}
