"""Agent execution state, lifecycle, and session abstractions for Workline ADK."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_USER = "WAITING_FOR_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


class AgentEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    agent_id: str
    event_type: str  # TOOL_CALL, TOOL_RESULT, STATE_CHANGE, DECISION_REQUIRED, ERROR, SUMMARY
    summary: str
    details: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Execution state tracked across agent tasks and persisted in SurrealDB."""
    execution_id: str
    session_id: str
    project_id: str
    agent_id: str
    agent_type: str
    task_id: str
    stage: str
    status: AgentStatus = AgentStatus.PENDING
    input_context: Dict[str, Any] = Field(default_factory=dict)
    output_summary: Optional[str] = None
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    events: List[AgentEvent] = Field(default_factory=list)
    requires_user_action: bool = False
    action_prompt: Optional[str] = None
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None


class WorklineSession(BaseModel):
    """Session connecting user, team, project, and agent executions."""
    session_id: str
    user_id: str
    team_id: Optional[str] = None
    project_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    active_execution_id: Optional[str] = None
    history: List[str] = Field(default_factory=list)
