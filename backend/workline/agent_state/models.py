"""
Pydantic data models for Agent Execution State, Checkpoints, Decisions, and Tool Executions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentRunStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    WAITING_FOR_INPUT = "WAITING_FOR_INPUT"
    WAITING_FOR_HUMAN = "WAITING_FOR_HUMAN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PAUSED = "PAUSED"


class ToolExecution(BaseModel):
    """Execution record for an individual agent tool call."""
    execution_id: str = Field(default_factory=lambda: f"tool_{uuid.uuid4().hex[:10]}")
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    duration_ms: Optional[float] = None
    redacted_fields: List[str] = Field(default_factory=list, description="Fields scrubbed for secret safety")


class AgentCheckpoint(BaseModel):
    """Checkpoint snapshot enabling pause, resume, and audit of agent state."""
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:10]}")
    run_id: str
    step_number: int
    state_snapshot: Dict[str, Any] = Field(default_factory=dict)
    memory_summary: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentDecision(BaseModel):
    """Explicit record of an agent decision, reasoning chain, and confidence."""
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:10]}")
    run_id: str
    action_type: str
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives_considered: List[str] = Field(default_factory=list)
    requires_human_approval: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AgentRun(BaseModel):
    """Aggregate lifecycle record for an autonomous agent execution."""
    run_id: str = Field(default_factory=lambda: f"run_{uuid.uuid4().hex[:10]}")
    agent_id: str
    project_id: Optional[str] = None
    status: AgentRunStatus = Field(default=AgentRunStatus.INITIALIZED)
    prompt: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    tool_executions: List[ToolExecution] = Field(default_factory=list)
    checkpoints: List[AgentCheckpoint] = Field(default_factory=list)
    decisions: List[AgentDecision] = Field(default_factory=list)
    final_output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    correlation_id: Optional[str] = None
