"""Agent task models, status lifecycles, and execution context."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.interoperability.capabilities import RiskLevel
from backend.workline.interoperability.provenance import TaskProvenance
from backend.workline.interoperability.security import ArtifactReference


class TaskStatus(str, Enum):
    """Lifecycle states of an external agent task."""
    PENDING = "PENDING"
    AUTHORIZED = "AUTHORIZED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    TIMEOUT = "TIMEOUT"
    REJECTED = "REJECTED"


class AuditEventType(str, Enum):
    """Audit events recorded throughout external agent lifecycle."""
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_DISCOVERED = "AGENT_DISCOVERED"
    AGENT_TASK_CREATED = "AGENT_TASK_CREATED"
    AGENT_TASK_AUTHORIZED = "AGENT_TASK_AUTHORIZED"
    AGENT_TASK_REJECTED = "AGENT_TASK_REJECTED"
    AGENT_TASK_STARTED = "AGENT_TASK_STARTED"
    AGENT_TASK_COMPLETED = "AGENT_TASK_COMPLETED"
    AGENT_TASK_FAILED = "AGENT_TASK_FAILED"
    AGENT_TASK_CANCELLED = "AGENT_TASK_CANCELLED"
    AGENT_RESULT_VALIDATED = "AGENT_RESULT_VALIDATED"


class InteroperabilityAuditEvent(BaseModel):
    """Immutable audit event record for external agent interactions."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_id: str
    team_id: str
    task_id: str
    agent_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: AuditEventType
    details: Dict[str, Any] = Field(default_factory=dict)


class TaskContext(BaseModel):
    """Minimal, capability-scoped task context delivered to external agents."""
    task_id: str
    project_id: str
    team_id: str
    capability: str
    input_parameters: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    artifact_references: List[ArtifactReference] = Field(default_factory=list)


class AgentTask(BaseModel):
    """Comprehensive representation of an external agent task execution."""
    task_id: str = Field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: str
    requesting_agent: str
    target_agent: str
    capability: str
    input_reference: Optional[Dict[str, Any]] = None
    output_reference: Optional[Dict[str, Any]] = None
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    idempotency_key: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    timeout: float = Field(default=30.0, description="Task timeout in seconds")
    error: Optional[str] = None
    provenance: Optional[TaskProvenance] = None
