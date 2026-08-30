"""
Data contracts and Pydantic schemas for ComponentPlanningAgent (Agent #7).
Defines BOM items, component requirements, compatibility validations, resource conflicts,
alternatives, passives, traceability, and 7-file export contracts.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


SelectionStatusLiteral = Literal["selected", "candidate", "pending"]

AlternativeCompatibilityLiteral = Literal[
    "drop_in",
    "electrically_compatible",
    "functionally_equivalent",
    "performance_alternative",
    "architecture_alternative",
    "partial_compatibility",
    "pending_validation",
]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration (Section 40)."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "ComponentPlanningAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class ProjectMeta(BaseModel):
    """Engineering project metadata."""

    project_id: Optional[str] = None
    title: str = Field(..., description="Project title or concept name.")
    description: Optional[str] = Field(default=None, description="Problem statement.")
    engineering_domain: Optional[str] = Field(default=None, description="Engineering discipline.")
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class ComponentRequirementItem(BaseModel):
    """Component requirement derived from system architecture (Section 7)."""

    requirement_id: str
    category: str
    quantity: int = 1
    required_specifications: Dict[str, Any] = Field(default_factory=dict)
    source_subsystem: str
    reason: str
    source_decision_ids: List[str] = Field(default_factory=list)


class ComponentAlternativeItem(BaseModel):
    """Alternative candidate component evaluation (Sections 18 & 19)."""

    alternative_id: str
    part_number: str
    manufacturer: str
    compatibility: AlternativeCompatibilityLiteral = "functionally_equivalent"
    differences: List[str] = Field(default_factory=list)
    reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    datasheet_url: Optional[str] = None


class BOMItem(BaseModel):
    """Core Bill of Materials item specification (Sections 9 & 25)."""

    bom_item_id: str
    line_number: int = 1
    category: str
    part_number: str
    manufacturer: str
    component_name: str
    description: str
    quantity: int = 1
    unit: str = "pcs"
    subsystem_id: str
    role: str
    selection_status: SelectionStatusLiteral = "selected"
    required_specifications: Dict[str, Any] = Field(default_factory=dict)
    known_specifications: Dict[str, Any] = Field(default_factory=dict)
    interfaces: List[str] = Field(default_factory=list)
    power_requirements: Dict[str, Any] = Field(default_factory=dict)
    mechanical_requirements: Dict[str, Any] = Field(default_factory=dict)
    software_requirements: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    datasheet_url: Optional[str] = None
    alternatives: List[ComponentAlternativeItem] = Field(default_factory=list)
    selection_reason: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source_evidence_ids: List[str] = Field(default_factory=list)
    validation_required: bool = False


class CompatibilityCheck(BaseModel):
    """Electrical, power, interface, mechanical, or software compatibility verification (Sections 11-13)."""

    check_id: str
    type: Literal["electrical", "power", "interface", "mechanical", "software", "thermal", "manufacturing"]
    status: Literal["passed", "warning", "failed", "unknown"] = "passed"
    description: str
    affected_items: List[str] = Field(default_factory=list)
    required_action: Optional[str] = None


class ResourceConflict(BaseModel):
    """Resource conflict detection (Section 14)."""

    conflict_id: str
    type: Literal[
        "interface_resource",
        "i2c_address",
        "uart_port",
        "gpio_channel",
        "pwm_channel",
        "adc_channel",
        "memory_capacity",
        "power_capacity",
        "bandwidth",
    ] = "interface_resource"
    description: str
    affected_components: List[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high"] = "medium"
    resolution: str
    validation_required: bool = True


class BOMValidationItem(BaseModel):
    """BOM validation requirement item (Section 32)."""

    validation_id: str
    type: Literal["electrical", "power", "interface", "mechanical", "software", "thermal", "manufacturing"]
    description: str
    affected_items: List[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high"] = "medium"
    status: Literal["required", "recommended", "passed", "failed", "unknown"] = "required"
    reason: str


class BOMUnknownItem(BaseModel):
    """Explicitly tracked technical unknown (Section 33)."""

    unknown_id: str
    description: str
    affected_items: List[str] = Field(default_factory=list)
    why_it_matters: str
    required_information: str
    blocking: bool = False


class BOMAssumptionItem(BaseModel):
    """Explicitly tracked engineering assumption (Section 34)."""

    assumption_id: str
    description: str
    affected_items: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_required: bool = True


class BOMTraceabilityItem(BaseModel):
    """Requirement-to-component-to-validation traceability lineage (Section 48)."""

    traceability_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    subsystem_ids: List[str] = Field(default_factory=list)
    component_requirement_ids: List[str] = Field(default_factory=list)
    bom_item_ids: List[str] = Field(default_factory=list)
    validation_ids: List[str] = Field(default_factory=list)


class BOMSummary(BaseModel):
    """Summary metrics for the engineering BOM (Section 24)."""

    total_line_items: int = 0
    selected_items: int = 0
    candidate_items: int = 0
    pending_items: int = 0
    subsystem_count: int = 0


class StructuredError(BaseModel):
    """Machine-readable error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class ComponentPlanningAgentInput(BaseModel):
    """Structured input contract for ComponentPlanningAgent (Section 4)."""

    project: ProjectMeta
    architecture: Dict[str, Any] = Field(
        default_factory=dict,
        description="Architecture metadata from Agent #6.",
    )
    subsystems: List[Dict[str, Any]] = Field(default_factory=list)
    component_roles: List[Dict[str, Any]] = Field(default_factory=list)
    interfaces: List[Dict[str, Any]] = Field(default_factory=list)
    power_domains: List[Dict[str, Any]] = Field(default_factory=list)
    data_flows: List[Dict[str, Any]] = Field(default_factory=list)
    control_flows: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    architecture_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    validation_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    engineering_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    research_facts: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional directory to export the 7 required BOM artifacts.",
    )
    execution_context: Optional[RequestContext] = None


class ComponentPlanningAgentOutput(BaseModel):
    """Structured output contract for ComponentPlanningAgent (Section 24)."""

    status: Literal["success", "error"] = "success"
    bom_id: str = "BOM-001"
    project_id: str = ""
    version: str = "1.0"
    summary: BOMSummary = Field(default_factory=BOMSummary)
    items: List[BOMItem] = Field(default_factory=list)
    component_requirements: List[ComponentRequirementItem] = Field(default_factory=list)
    subsystems: List[Dict[str, Any]] = Field(default_factory=list)
    conflicts: List[ResourceConflict] = Field(default_factory=list)
    compatibility_checks: List[CompatibilityCheck] = Field(default_factory=list)
    alternatives: List[ComponentAlternativeItem] = Field(default_factory=list)
    validation_requirements: List[BOMValidationItem] = Field(default_factory=list)
    unknowns: List[BOMUnknownItem] = Field(default_factory=list)
    assumptions: List[BOMAssumptionItem] = Field(default_factory=list)
    traceability: List[BOMTraceabilityItem] = Field(default_factory=list)
    structured_bom_markdown: str = ""
    warnings: List[str] = Field(default_factory=list)
    errors: List[StructuredError] = Field(default_factory=list)
