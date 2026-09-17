"""Task schemas, lifecycle states, and context propagation models for Agent Control Fabric."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    ROUTED = "ROUTED"
    AUTHORIZED = "AUTHORIZED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"
    CANCELLED = "CANCELLED"
    RETRYING = "RETRYING"


class TaskContext(BaseModel):
    """Immutable execution context propagated across the entire call path."""

    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    parent_task_id: Optional[str] = None
    workflow_id: Optional[str] = None
    project_id: str = Field(default="default")
    user_id: str = Field(default="system")
    organization_id: Optional[str] = None
    authorization_token: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class FabricTask(BaseModel):
    """Unit of work submitted to and tracked by the Control Fabric."""

    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    context: TaskContext
    target_capability: Optional[str] = None
    target_agent_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    state: TaskState = Field(default=TaskState.PENDING)
    retries_attempted: int = 0
    max_retries: int = 3
    timeout_seconds: float = 60.0
    idempotency_key: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    events: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
