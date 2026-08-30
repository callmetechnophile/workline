"""
Pydantic data contracts and schemas for EngineeringExecutionAgent (Agent #11).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ExecutionStatusLiteral = Literal[
    "pending",
    "authorized",
    "running",
    "completed",
    "failed",
    "denied",
    "revoked",
    "expired",
    "blocked",
    "partial",
    "success",
]

ToolTypeLiteral = Literal[
    "filesystem",
    "filesystem.read",
    "filesystem.write",
    "filesystem.create",
    "filesystem.modify",
    "filesystem.delete",
    "shell",
    "git",
    "python",
    "node",
    "compiler",
    "test_runner",
    "build_system",
    "simulation",
    "container",
    "delegate",
]

OperationTypeLiteral = Literal[
    "read",
    "create",
    "modify",
    "delete",
    "execute",
    "test",
    "build",
    "commit",
    "push",
    "deploy",
]


class AuthorizedExecution(BaseModel):
    """Explicit cryptographic authorization record (Section 6 & 8)."""

    authorization_id: str
    parent_agent_id: str = "ResearchOrchestrator"
    authorized_agent_id: str = "EngineeringExecutionAgent"
    scope: Dict[str, Any] = Field(default_factory=dict)
    allowed_tasks: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_paths: List[str] = Field(default_factory=list)
    allowed_operations: List[str] = Field(default_factory=list)
    expires_at: Optional[str] = None
    revoked: bool = False
    parent_receipt: Optional[Dict[str, Any]] = None


class ExecutionTask(BaseModel):
    """Granular work package execution task (Sections 10, 24, 26)."""

    task_id: str
    work_package_id: str = "WP-001"
    title: str
    description: str = ""
    task_type: str = "code"  # code, firmware, hardware, pcb, simulation, aiml, testing, configuration, documentation, build, integration
    dependencies: List[str] = Field(default_factory=list)
    allowed_paths: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_operations: List[str] = Field(default_factory=list)
    command: Optional[str] = None
    target_file: Optional[str] = None
    file_content: Optional[str] = None
    operation: Optional[str] = None
    expected_outputs: List[str] = Field(default_factory=list)
    status: ExecutionStatusLiteral = "pending"
    error: Optional[str] = None
    max_retries: int = 1


class ToolCallRecord(BaseModel):
    """Detailed tool invocation telemetry and cryptographic receipts (Section 21 & 22)."""

    tool_call_id: str
    task_id: str
    tool: str
    operation: str
    resource: str
    status: Literal["success", "failed", "denied"]
    armoriq_receipt_id: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    duration_ms: float = 0.0


class ExecutionReceipt(BaseModel):
    """Cryptographic ArmorIQ receipt representation."""

    receipt_id: str
    timestamp: float
    agent: str
    scope: List[str]
    parent_receipt_id: Optional[str] = None
    signature: str


class ExecutionAuditItem(BaseModel):
    """Machine-readable execution audit record (Section 53)."""

    audit_id: str
    timestamp: str
    project_id: str
    execution_id: str
    task_id: str
    agent_id: str
    parent_agent_id: Optional[str] = None
    authorization_id: str
    delegation_chain: List[str] = Field(default_factory=list)
    tool: str
    operation: str
    resource: str
    status: str
    armoriq_receipt_id: Optional[str] = None
    result_hash: Optional[str] = None


class ExecutionGraphNode(BaseModel):
    """Node in the execution dependency & authorization graph (Section 54)."""

    id: str
    type: str  # user, agent, authorization, delegation, task, tool, operation, resource, result, receipt
    label: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExecutionGraphEdge(BaseModel):
    """Edge in the execution dependency & authorization graph (Section 54)."""

    source: str
    target: str
    relation: str  # authorized_by, delegated_to, executes, invokes, accesses, produces, verified_by, blocked_by, depends_on


class ExecutionGraph(BaseModel):
    """Graph structure capturing the entire execution lineage (Section 54)."""

    nodes: List[ExecutionGraphNode] = Field(default_factory=list)
    edges: List[ExecutionGraphEdge] = Field(default_factory=list)


class DelegationObject(BaseModel):
    """Structured ArmorIQ delegation object (Section 19)."""

    delegation_id: str
    parent_agent_id: str
    child_agent_id: str
    project_id: str
    task_id: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_paths: List[str] = Field(default_factory=list)
    allowed_operations: List[str] = Field(default_factory=list)
    expires_at: Optional[str] = None
    constraints: List[str] = Field(default_factory=list)
    armoriq_receipt: Optional[Dict[str, Any]] = None


class EngineeringExecutionContext(BaseModel):
    """Execution context and identities."""

    user_id: str = "user_001"
    project_id: str = "proj_001"
    agent_id: str = "EngineeringExecutionAgent"
    parent_agent_id: Optional[str] = "ResearchOrchestrator"
    execution_id: Optional[str] = None


class EngineeringExecutionAgentInput(BaseModel):
    """Input contract for Agent #11 (Section 6)."""

    project: Dict[str, Any]
    implementation_plan: Dict[str, Any]
    validation: Dict[str, Any]
    architecture: Dict[str, Any] = Field(default_factory=dict)
    bom: Dict[str, Any] = Field(default_factory=dict)
    procurement: Dict[str, Any] = Field(default_factory=dict)
    authorized_execution: AuthorizedExecution
    execution_context: Optional[EngineeringExecutionContext] = None
    project_root_dir: Optional[str] = None
    output_dir: Optional[str] = None
    dry_run: bool = False
    single_task_id: Optional[str] = None
    resume_execution_id: Optional[str] = None


class EngineeringExecutionAgentOutput(BaseModel):
    """Output contract for Agent #11 (Section 61)."""

    status: ExecutionStatusLiteral
    execution_id: str
    project_id: str
    authorization_id: str
    completed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    failed_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    blocked_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    denied_actions: List[Dict[str, Any]] = Field(default_factory=list)
    tool_calls: List[ToolCallRecord] = Field(default_factory=list)
    armoriq_receipts: List[Dict[str, Any]] = Field(default_factory=list)
    audit_trail: List[ExecutionAuditItem] = Field(default_factory=list)
    execution_graph: ExecutionGraph = Field(
        default_factory=lambda: ExecutionGraph(nodes=[], edges=[])
    )
    changed_files: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    structured_report_markdown: str = ""
