"""
Workline AI — Contextual Comments Models and Mentions.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ContextComment(BaseModel):
    """Contextual comment attached to an engineering artifact or project."""
    id: str = Field(default_factory=lambda: f"CMT-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    parent_type: str = "project"  # "task", "bom_item", "component", "document", "decision", "analysis", "datasheet", "project"
    parent_id: str = "general"
    author_id: str
    author_name: str
    content: str
    mentions: List[str] = Field(default_factory=list)  # list of mentioned user_ids or usernames
    reply_to_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_edited: bool = False
    is_deleted: bool = False


class CreateCommentRequest(BaseModel):
    """Payload to post a contextual comment."""
    project_id: str
    parent_type: Optional[str] = "project"
    parent_id: Optional[str] = "general"
    content: str
    reply_to_id: Optional[str] = None


class UpdateCommentRequest(BaseModel):
    """Payload to edit an existing comment."""
    content: str
