"""
Pydantic data contracts and graph node/edge schemas for EngineeringKnowledgeGraphAgent (Agent #13).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ProjectStateLiteral = Literal[
    "research",
    "design",
    "bom",
    "procurement",
    "validation",
    "planning",
    "implementation",
    "qa",
    "verified",
    "blocked",
    "archived",
]


class BaseGraphNode(BaseModel):
    """Base schema for all SurrealDB graph nodes."""

    id: str
    type: str
    project_id: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


class UserNode(BaseModel):
    """User account entity with multi-tenant isolation (Section 7)."""

    id: str
    type: str = "user"
    external_user_id: str
    display_name: str
    created_at: str
    updated_at: Optional[str] = None


class ProjectNode(BaseModel):
    """Project entity with ownership and state (Section 8)."""

    id: str
    type: str = "project"
    name: str
    description: str = ""
    status: ProjectStateLiteral = "research"
    owner_id: str
    team_id: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


class RequirementNode(BaseModel):
    """Engineering requirement entity (Section 10)."""

    id: str
    type: str = "requirement"
    project_id: str
    title: str
    description: str
    category: str = "functional"
    priority: Literal["critical", "high", "medium", "low"] = "high"
    source: str = "synthesis"
    status: str = "active"
    created_at: str
    updated_at: Optional[str] = None


class ResearchNode(BaseModel):
    """Research evidence item (Section 12)."""

    id: str
    type: str = "research"
    project_id: str
    title: str
    source: str
    url: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    publication: Optional[str] = None
    date: Optional[str] = None
    summary: str = ""
    relevance: Optional[float] = None
    confidence: Optional[float] = None
    agent_id: str = "ResearchPaperAgent"
    created_at: str


class EngineeringDecisionNode(BaseModel):
    """Architecture / design tradeoff decision (Section 14)."""

    id: str
    type: str = "engineering_decision"
    project_id: str
    title: str
    decision: str
    reasoning: str
    alternatives_considered: List[str] = Field(default_factory=list)
    selected_option: str
    confidence: Optional[float] = None
    agent_id: str = "EngineeringSynthesisAgent"
    created_at: str
    supersedes: Optional[str] = None


class ArchitectureNode(BaseModel):
    """System architecture definition (Section 16)."""

    id: str
    type: str = "architecture"
    project_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    status: str = "validated"
    created_at: str
    updated_at: Optional[str] = None


class SubsystemNode(BaseModel):
    """Subsystem block (Section 17)."""

    id: str
    type: str = "subsystem"
    project_id: str
    architecture_id: str
    name: str
    description: str = ""
    status: str = "active"


class InterfaceNode(BaseModel):
    """Interface / electrical bus / protocol connection (Section 18)."""

    id: str
    type: str = "interface"
    project_id: str
    name: str
    protocol: str
    source: str
    destination: str
    voltage: Optional[str] = None
    direction: Optional[str] = None
    description: str = ""


class ComponentNode(BaseModel):
    """Physical / electronic component with stable identity (Section 19 & 20)."""

    id: str
    type: str = "component"
    part_number: str
    manufacturer: str
    category: str
    description: str = ""
    datasheet_url: Optional[str] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: Optional[str] = None


class BOMNode(BaseModel):
    """Bill of Materials header (Section 22)."""

    id: str
    type: str = "bom"
    project_id: str
    version: str = "1.0.0"
    status: str = "optimized"
    created_at: str
    updated_at: Optional[str] = None


class BOMItemNode(BaseModel):
    """Individual line item in BOM (Section 23)."""

    id: str
    type: str = "bom_item"
    project_id: str
    bom_id: str
    component_id: str
    quantity: int = 1
    reference_designators: List[str] = Field(default_factory=list)
    subsystem_id: Optional[str] = None
    status: str = "active"
    created_at: str


class SupplierNode(BaseModel):
    """Component vendor / distributor (Section 24)."""

    id: str
    type: str = "supplier"
    name: str
    location: Dict[str, Any] = Field(default_factory=dict)
    website: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


class SupplierOfferNode(BaseModel):
    """Live pricing and inventory quote from vendor (Section 25)."""

    id: str
    type: str = "supplier_offer"
    supplier_id: str
    component_id: str
    part_number: str
    unit_price: Optional[float] = None
    currency: str = "INR"
    availability: Optional[str] = "IN_STOCK"
    minimum_order_quantity: Optional[int] = 1
    lead_time_days: Optional[int] = 3
    source_url: Optional[str] = None
    confidence: Optional[float] = None
    data_timestamp: str


class ProcurementPlanNode(BaseModel):
    """Optimized purchasing strategy (Section 26)."""

    id: str
    type: str = "procurement_plan"
    project_id: str
    strategy: str = "balanced"
    total_product_cost: Optional[float] = None
    total_shipping_cost: Optional[float] = None
    known_landed_cost: Optional[float] = None
    supplier_count: Optional[int] = None
    created_at: str


class ShippingOptionNode(BaseModel):
    """Logistics rate and transit quote (Section 28)."""

    id: str
    type: str = "shipping_option"
    supplier_id: str
    origin: Dict[str, Any] = Field(default_factory=dict)
    destination: Dict[str, Any] = Field(default_factory=dict)
    distance_km: Optional[float] = None
    carrier: Optional[str] = None
    service: Optional[str] = None
    shipping_cost: Optional[float] = None
    currency: str = "INR"
    delivery_days: Optional[int] = None
    data_timestamp: str
    confidence: Optional[float] = None


class ImplementationPlanNode(BaseModel):
    """Execution plan definition (Section 29)."""

    id: str
    type: str = "implementation_plan"
    project_id: str
    version: str = "1.0.0"
    status: str = "approved"
    created_at: str


class WorkPackageNode(BaseModel):
    """Logical grouping of tasks (Section 30)."""

    id: str
    type: str = "work_package"
    project_id: str
    plan_id: str
    name: str
    category: str
    description: str = ""
    status: str = "active"
    priority: str = "high"
    created_at: str


class ImplementationTaskNode(BaseModel):
    """Individual work package task (Section 31)."""

    id: str
    type: str = "implementation_task"
    project_id: str
    package_id: str
    title: str
    description: str = ""
    task_type: str = "firmware"
    priority: str = "high"
    status: str = "completed"
    blocking: bool = False
    created_at: str
    updated_at: Optional[str] = None


class ExecutionNode(BaseModel):
    """Agent #11 tool execution session (Section 32)."""

    id: str
    type: str = "execution"
    execution_id: str
    project_id: str
    agent_id: str = "EngineeringExecutionAgent"
    status: str = "success"
    started_at: str
    completed_at: Optional[str] = None


class ProjectFileNode(BaseModel):
    """Source file created or modified (Section 33)."""

    id: str
    type: str = "project_file"
    project_id: str
    path: str
    file_type: str = "python"
    hash: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None


class TestNode(BaseModel):
    """Automated test definition (Section 34)."""

    id: str
    type: str = "test"
    project_id: str
    name: str
    test_type: str = "unit"
    command: Optional[str] = None
    expected_result: str = "PASS"
    created_at: str


class TestResultNode(BaseModel):
    """Telemetry from test execution (Section 35)."""

    id: str
    type: str = "test_result"
    test_id: str
    status: Literal["PASS", "FAIL", "SKIPPED", "ERROR"] = "PASS"
    passed: Optional[int] = 1
    failed: Optional[int] = 0
    duration: Optional[float] = None
    timestamp: str
    evidence_id: Optional[str] = None


class EvidenceNode(BaseModel):
    """Cryptographically anchored proof artifact (Section 36)."""

    id: str
    type: str = "evidence"
    evidence_type: str
    source: str
    reference: str = ""
    timestamp: str
    confidence: Optional[float] = None


class ValidationNode(BaseModel):
    """Agent #9 rule check (Section 37)."""

    id: str
    type: str = "validation"
    validation_id: str
    category: str
    status: str = "PASS"
    severity: str = "CRITICAL"
    title: str
    description: str = ""
    blocking: bool = False
    created_at: str


class EngineeringFailureNode(BaseModel):
    """Defect, conflict, or validation issue (Section 38)."""

    id: str
    type: str = "engineering_failure"
    category: str
    severity: str = "CRITICAL"
    description: str
    status: Literal["open", "resolved", "accepted"] = "open"
    created_at: str
    resolved_at: Optional[str] = None


class AgentNode(BaseModel):
    """Agent registry record (Section 45)."""

    id: str
    type: str = "agent"
    agent_name: str
    agent_version: str = "1.0.0"
    capabilities: List[str] = Field(default_factory=list)
    created_at: str


class AuthorizationNode(BaseModel):
    """ArmorIQ execution grant (Section 47)."""

    id: str
    type: str = "authorization"
    authorization_id: str
    project_id: str
    agent_id: str
    scope: Dict[str, Any] = Field(default_factory=dict)
    status: str = "active"
    created_at: str
    expires_at: Optional[str] = None


class ExecutionReceiptNode(BaseModel):
    """HMAC-signed ArmorIQ invocation receipt (Section 50)."""

    id: str
    type: str = "execution_receipt"
    receipt_id: str
    execution_id: str
    timestamp: str
    status: str = "valid"
    provider: str = "ArmorIQ"


class ProjectStateNode(BaseModel):
    """Current state of project lifecycle (Section 41 & 43)."""

    id: str
    type: str = "project_state"
    project_id: str
    current_state: ProjectStateLiteral = "research"
    previous_state: Optional[ProjectStateLiteral] = None
    transition_reason: str = "Initial project initialization."
    transition_source: Literal["agent", "validation", "qa", "system"] = "system"
    timestamp: str


class StateEventNode(BaseModel):
    """Historical state change event (Section 44)."""

    id: str
    type: str = "state_event"
    project_id: str
    from_state: Optional[str] = None
    to_state: str
    reason: str
    source: str
    timestamp: str


class AuditEvent(BaseModel):
    """Graph mutation audit record (Section 91)."""

    audit_id: str
    project_id: str
    agent_id: str = "EngineeringKnowledgeGraphAgent"
    operation: Literal["create", "update", "upsert", "link"] = "create"
    object_type: str
    object_id: str
    timestamp: str
    source_artifact: str = "ingestion"
    status: Literal["success", "failed"] = "success"


class GraphEdge(BaseModel):
    """Relationship connecting two graph nodes."""

    id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: str


# =============================================================================
# Graph Query and Impact Schemas
# =============================================================================


class RequirementTraceResult(BaseModel):
    """Complete requirement-to-validation lineage trace (Section 53 & 74)."""

    requirement_id: str
    title: str
    decisions: List[str] = Field(default_factory=list)
    architectures: List[str] = Field(default_factory=list)
    subsystems: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    boms: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)
    executions: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    validations: List[str] = Field(default_factory=list)
    qa_status: str = "PASS"


class ComponentImpactResult(BaseModel):
    """Impact analysis when a component is modified or unavailable (Section 54, 56, 75)."""

    component_id: str
    part_number: str
    affected_subsystems: List[str] = Field(default_factory=list)
    affected_interfaces: List[str] = Field(default_factory=list)
    affected_bom_items: List[str] = Field(default_factory=list)
    affected_procurement_plans: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    affected_files: List[str] = Field(default_factory=list)
    affected_tests: List[str] = Field(default_factory=list)
    affected_requirements: List[str] = Field(default_factory=list)


class RequirementImpactResult(BaseModel):
    """Impact analysis when a requirement changes (Section 55)."""

    requirement_id: str
    affected_decisions: List[str] = Field(default_factory=list)
    affected_subsystems: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    affected_tests: List[str] = Field(default_factory=list)
    revalidation_required: bool = True


class ArchitectureImpactResult(BaseModel):
    """Impact analysis when a subsystem changes (Section 57)."""

    subsystem_id: str
    affected_interfaces: List[str] = Field(default_factory=list)
    affected_components: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    affected_tests: List[str] = Field(default_factory=list)


class ProjectTimelineEvent(BaseModel):
    """Timeline entry across engineering lifecycle (Section 60)."""

    timestamp: str
    category: str
    title: str
    details: str
    source_agent: str


class EngineeringKnowledgeGraphInput(BaseModel):
    """Ingestion input bundle for Agent #13."""

    user_id: str = "user_001"
    project: Dict[str, Any]
    requirements: List[Dict[str, Any]] = Field(default_factory=list)
    research: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    architecture: Dict[str, Any] = Field(default_factory=dict)
    bom: Dict[str, Any] = Field(default_factory=dict)
    procurement: Dict[str, Any] = Field(default_factory=dict)
    validation: Dict[str, Any] = Field(default_factory=dict)
    implementation_plan: Dict[str, Any] = Field(default_factory=dict)
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    verification_qa: Dict[str, Any] = Field(default_factory=dict)
    output_dir: Optional[str] = None


class EngineeringKnowledgeGraphOutput(BaseModel):
    """Execution output contract for Agent #13 (Section 103)."""

    status: Literal["success", "partial", "failed"]
    project_id: str
    graph_operation_id: str
    nodes_created: int = 0
    nodes_updated: int = 0
    relationships_created: int = 0
    duplicates_prevented: int = 0
    current_state: ProjectStateLiteral = "research"
    state_transition: Optional[str] = None
    consistency_status: Literal["PASS", "FAIL"] = "PASS"
    audit_events: List[AuditEvent] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    structured_report_markdown: str = ""
