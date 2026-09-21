"""
Workline AI — Unified Activity and Audit Models.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ActorType(str, Enum):
    """Classification of event initiator."""
    USER = "USER"
    AGENT = "AGENT"
    SYSTEM = "SYSTEM"


class UnifiedActivityEvent(BaseModel):
    """Authoritative immutable activity & audit trail record."""
    id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: Optional[str] = None
    actor_type: ActorType
    actor_id: str
    actor_name: str
    event_type: str  # e.g., "BOM_UPDATED", "TASK_CREATED", "AGENT_DELEGATED", "DECISION_APPROVED"
    target_type: str  # "bom", "task", "agent", "decision", "datasheet", "comment", "member"
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    summary: str
    receipt_id: Optional[str] = None  # ArmorIQ delegation receipt ID if executed via agent
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LogActivityRequest(BaseModel):
    """Payload to record an activity event."""
    project_id: str
    team_id: Optional[str] = None
    actor_type: ActorType = ActorType.USER
    actor_id: str
    actor_name: Optional[str] = None
    event_type: str
    target_type: str
    target_id: Optional[str] = None
    target_name: Optional[str] = None
    summary: str
    receipt_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
