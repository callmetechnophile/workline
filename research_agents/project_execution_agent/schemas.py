"""
Pydantic schemas and data contracts for ProjectExecutionAgent (Agent #10).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
import uuid


TaskTypeLiteral = Literal[
    "code",
    "firmware",
    "hardware",
    "pcb",
    "simulation",
    "aiml",
    "testing",
    "configuration",
    "documentation",
    "build",
    "integration",
]

PriorityLiteral = Literal["low", "medium", "high", "critical"]
PhaseLiteral = Literal["INITIATION", "DESIGN", "IMPLEMENTATION", "VERIFICATION", "DEPLOYMENT"]


class ProjectMeta(BaseModel):
    """Project metadata reference."""
    project_id: str = Field(default_factory=lambda: f"proj_{uuid.uuid4().hex[:6]}")
    title: str = "Engineering Project"
    engineering_domain: str = "General Engineering"
    description: Optional[str] = None


class PlanningTask(BaseModel):
    """Discrete execution task within a work package (Agent #10 -> Agent #11)."""

    task_id: str
    work_package_id: str
    title: str
    description: str = ""
    task_type: TaskTypeLiteral = "code"
    priority: PriorityLiteral = "medium"
    estimated_hours: float = 4.0
    dependencies: List[str] = Field(default_factory=list)
    allowed_paths: List[str] = Field(default_factory=list)
    allowed_tools: List[str] = Field(default_factory=list)
    allowed_operations: List[str] = Field(default_factory=list)
    command: Optional[str] = None
    target_file: Optional[str] = None
    file_content: Optional[str] = None
    expected_outputs: List[str] = Field(default_factory=list)
    validation_criteria: List[str] = Field(default_factory=list)
    status: str = "pending"


class WorkPackage(BaseModel):
    """Work package grouping discrete implementation tasks."""

    work_package_id: str
    title: str
    description: str = ""
    phase: PhaseLiteral = "IMPLEMENTATION"
    estimated_hours: float = 0.0
    deliverables: List[str] = Field(default_factory=list)
    tasks: List[PlanningTask] = Field(default_factory=list)


class DependencyDAG(BaseModel):
    """Directed Acyclic Graph of task dependencies with topological order."""

    nodes: List[str] = Field(default_factory=list)
    edges: List[Dict[str, str]] = Field(default_factory=list)
    topological_order: List[str] = Field(default_factory=list)
    critical_path: List[str] = Field(default_factory=list)
    has_cycle: bool = False
    cycle_nodes: List[str] = Field(default_factory=list)


class ImplementationPlan(BaseModel):
    """Structured Implementation Plan produced by Agent #10 for Agent #11."""

    plan_id: str = Field(default_factory=lambda: f"PLAN-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    title: str
    engineering_domain: str
    created_at: str = ""
    work_packages: List[WorkPackage] = Field(default_factory=list)
    all_tasks: List[PlanningTask] = Field(default_factory=list)
    dag: DependencyDAG = Field(default_factory=DependencyDAG)
    total_estimated_hours: float = 0.0
    execution_readiness: bool = True
    blocking_reasons: List[str] = Field(default_factory=list)


class ProjectExecutionAgentInput(BaseModel):
    """Input payload for ProjectExecutionAgent."""

    project: Optional[Dict[str, Any]] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    engineering_domain: Optional[str] = None
    architecture: Optional[Dict[str, Any]] = None
    bom: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    requirements: Optional[List[Any]] = None
    decisions: Optional[List[Any]] = None
    output_dir: Optional[str] = None


class ProjectExecutionAgentOutput(BaseModel):
    """Output contract for ProjectExecutionAgent."""

    agent_id: str = "Agent #10"
    agent_name: str = "ProjectExecutionAgent"
    status: Literal["success", "blocked", "failed"] = "success"
    project_id: str
    plan_id: str
    implementation_plan: ImplementationPlan
    work_package_count: int
    task_count: int
    critical_path_length: int
    structured_markdown_report: str
    execution_readiness: bool
    execution_duration_seconds: float = 0.0
