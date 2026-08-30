"""
Pydantic data schemas and contracts for ProjectLifecycleOrchestrator (Agent #14).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


LifecycleStateLiteral = Literal[
    "RESEARCH",
    "SYNTHESIS",
    "ARCHITECTURE",
    "BOM",
    "PROCUREMENT",
    "VALIDATION",
    "PLANNING",
    "IMPLEMENTATION",
    "QA",
    "VERIFIED",
    "BLOCKED",
    "AWAITING_HUMAN",
    "ARCHIVED",
]

ActionTypeLiteral = Literal[
    "RESEARCH",
    "SYNTHESIZE",
    "DESIGN",
    "GENERATE_BOM",
    "OPTIMIZE_BOM",
    "VALIDATE",
    "PLAN_IMPLEMENTATION",
    "EXECUTE",
    "VERIFY",
    "PERSIST",
    "REVALIDATE",
    "REQUEST_HUMAN_INPUT",
    "WAIT_FOR_RESOURCE",
    "BLOCK",
    "COMPLETE",
]


class AgentDescriptor(BaseModel):
    """Registered capability record for an agent in WorkflowGuide AI (Section 14)."""

    agent_id: str
    agent_name: str
    capabilities: List[str] = Field(default_factory=list)
    input_schema: str = "PydanticBase"
    output_schema: str = "PydanticBase"
    required_authorization: List[str] = Field(default_factory=list)
    execution_level: Literal["read_only", "planning", "isolated_execution", "privileged_execution"] = "read_only"
    status: Literal["available", "busy", "disabled", "error"] = "available"
    version: str = "1.0.0"


class NextAction(BaseModel):
    """Prescribed next engineering workflow action (Section 11)."""

    action_id: str
    project_id: str
    current_state: LifecycleStateLiteral
    next_state: LifecycleStateLiteral
    action_type: ActionTypeLiteral
    target_agent: str
    reason: str
    blocking_conditions: List[str] = Field(default_factory=list)
    required_inputs: List[str] = Field(default_factory=list)
    required_authorization: List[str] = Field(default_factory=list)
    human_approval_required: bool = False
    priority: Literal["critical", "high", "medium", "low"] = "high"


class BlockerObject(BaseModel):
    """Detailed blocker record halting workflow progression (Section 18)."""

    blocker_id: str
    type: str
    severity: Literal["critical", "high", "medium", "low"] = "high"
    source: str
    affected_project: str
    affected_tasks: List[str] = Field(default_factory=list)
    resolution: str
    requires_human: bool = False


class HumanRequestObject(BaseModel):
    """Human decision request for material changes or escalations (Section 24)."""

    request_id: str
    project_id: str
    reason: str
    requested_decision: str
    affected_objects: List[str] = Field(default_factory=list)
    risk: str
    options: List[str] = Field(default_factory=list)
    recommended_option: Optional[str] = None
    status: Literal["pending", "approved", "rejected"] = "pending"


class StaleObject(BaseModel):
    """Marker for invalidated or stale downstream artifacts (Section 37)."""

    artifact_id: str
    artifact_type: str
    superseded_by: Optional[str] = None
    status: Literal["stale", "invalidated"] = "stale"
    reason: str
    timestamp: str


class DecisionObject(BaseModel):
    """Auditable orchestration decision log (Section 47)."""

    decision_id: str
    project_id: str
    current_state: LifecycleStateLiteral
    action: str
    target_agent: str
    reason: str
    evidence_refs: List[str] = Field(default_factory=list)
    authorization_required: bool = True
    human_approval_required: bool = False
    timestamp: str


class ProjectHealthObject(BaseModel):
    """Comprehensive project engineering health summary (Section 59)."""

    project_id: str
    state: LifecycleStateLiteral
    health: Literal["healthy", "warning", "blocked"]
    requirements_status: str
    architecture_status: str
    bom_status: str
    implementation_status: str
    qa_status: str
    blocking_issues: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    next_action: Optional[Dict[str, Any]] = None


class RevalidationPlan(BaseModel):
    """Scoped revalidation plan for targeted change propagation (Section 35)."""

    trigger_artifact: str
    trigger_type: str
    affected_subsystems: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    affected_tests: List[str] = Field(default_factory=list)
    required_stages: List[LifecycleStateLiteral] = Field(default_factory=list)
    human_approval_needed: bool = False


class OrchestrationRun(BaseModel):
    """Complete record of an orchestration evaluation cycle (Section 45 & 67)."""

    run_id: str
    project_id: str
    started_at: str
    completed_at: Optional[str] = None
    current_state: LifecycleStateLiteral
    health: Literal["healthy", "warning", "blocked"] = "healthy"
    next_action: Optional[NextAction] = None
    actions_executed: List[str] = Field(default_factory=list)
    actions_pending: List[str] = Field(default_factory=list)
    blockers: List[BlockerObject] = Field(default_factory=list)
    human_requests: List[HumanRequestObject] = Field(default_factory=list)
    agent_results: List[Dict[str, Any]] = Field(default_factory=list)
    authorization_events: List[Dict[str, Any]] = Field(default_factory=list)
    state_transitions: List[str] = Field(default_factory=list)
    status: Literal["running", "paused", "blocked", "completed", "failed"] = "running"
    completed: bool = False


class OrchestrationInput(BaseModel):
    """Input parameters for an orchestration run."""

    project_id: str
    user_id: str = "user_001"
    override_action: Optional[str] = None
    force_revalidation: bool = False
    output_dir: Optional[str] = None


class OrchestrationOutput(BaseModel):
    """Output bundle returned by ProjectLifecycleOrchestrator."""

    run: OrchestrationRun
    health: ProjectHealthObject
    next_action: Optional[NextAction] = None
    structured_report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
