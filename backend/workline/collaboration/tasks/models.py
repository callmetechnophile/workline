"""
Workline AI — Collaboration Task Models and Enums.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task workflow states."""
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    IN_REVIEW = "IN_REVIEW"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TaskPriority(str, Enum):
    """Task urgency levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RelatedArtifact(BaseModel):
    """Link to physical or analytical engineering artifacts."""
    artifact_type: str  # "COMPONENT", "BOM", "ANALYSIS", "DATASHEET", "DECISION", "WIRING", "SCHEMATIC"
    artifact_id: str
    artifact_name: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class CollaborationTask(BaseModel):
    """Engineering task entity with artifact linkage."""
    id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    creator_id: str
    creator_name: Optional[str] = None
    due_date: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    related_artifact: Optional[RelatedArtifact] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CreateTaskRequest(BaseModel):
    """Payload to create an engineering task."""
    project_id: str
    team_id: Optional[str] = None
    title: str
    description: Optional[str] = ""
    status: Optional[TaskStatus] = TaskStatus.TODO
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    due_date: Optional[str] = None
    labels: Optional[List[str]] = None
    related_artifact: Optional[RelatedArtifact] = None


class UpdateTaskRequest(BaseModel):
    """Payload to update an engineering task."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[str] = None
    assignee_name: Optional[str] = None
    due_date: Optional[str] = None
    labels: Optional[List[str]] = None
    related_artifact: Optional[RelatedArtifact] = None
