"""
Workline AI — Centralized Notifications Models.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class NotificationType(str, Enum):
    """Types of collaboration notifications."""
    MENTION = "MENTION"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_UPDATED = "TASK_UPDATED"
    JOIN_REQUEST = "JOIN_REQUEST"
    INVITATION = "INVITATION"
    APPROVAL_REQUEST = "APPROVAL_REQUEST"
    APPROVAL_RESULT = "APPROVAL_RESULT"
    COMMENT = "COMMENT"
    AGENT_COMPLETED = "AGENT_COMPLETED"
    AGENT_FAILED = "AGENT_FAILED"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    IMPORTANT_PROJECT_CHANGE = "IMPORTANT_PROJECT_CHANGE"


class Notification(BaseModel):
    """Centralized notification entity."""
    id: str = Field(default_factory=lambda: f"NOTIF-{uuid.uuid4().hex[:8].upper()}")
    recipient_id: str
    project_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    related_type: Optional[str] = None  # "task", "comment", "decision", "approval", "membership_request"
    related_id: Optional[str] = None
    read: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CreateNotificationRequest(BaseModel):
    """Payload to dispatch a notification."""
    recipient_id: str
    project_id: Optional[str] = None
    type: NotificationType
    title: str
    message: str
    related_type: Optional[str] = None
    related_id: Optional[str] = None
