"""
Data contracts and Pydantic schemas for EngineeringArchitectureAgent (Agent #6).
Defines subsystems, component roles, interfaces, power domains, data flows, control flows,
feedback loops, software architecture, dependency graphs, block diagrams, architecture graphs, and report schemas.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ComponentStatusLiteral = Literal["mandatory", "recommended", "optional", "alternative", "future", "pending"]

InterfaceTypeLiteral = Literal[
    "I2C",
    "SPI",
    "UART",
    "CAN",
    "USB",
    "Ethernet",
    "Wi-Fi",
    "Bluetooth",
    "GPIO",
    "PWM",
    "ADC",
    "DAC",
    "MIPI",
    "CSI",
    "DSI",
    "PCIe",
    "I2S",
    "SDIO",
    "Power",
    "Mechanical",
    "Thermal",
]

DependencyTypeLiteral = Literal["electrical", "software", "mechanical", "communication", "power", "thermal"]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "EngineeringArchitectureAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class ProjectMeta(BaseModel):
    """Engineering project scope, requirements, and constraints."""

    project_id: Optional[str] = None
    title: str = Field(..., description="Project title or concept name.")
    description: Optional[str] = Field(default=None, description="Detailed problem statement.")
    engineering_domain: Optional[str] = Field(default=None, description="Engineering discipline.")
    objectives: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    budget: Optional[str] = None
    timeline: Optional[str] = None


class SubsystemItem(BaseModel):
    """Logical subsystem item with explicit boundaries and responsibilities (Section 7)."""

    subsystem_id: str
    name: str
    purpose: str
    responsibilities: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    interfaces: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    validation_requirements: List[str] = Field(default_factory=list)


class ComponentRoleItem(BaseModel):
    """Mapping of hardware/software components into architecture roles (Section 8 & 9)."""

    component: str
    role: str
    subsystem_id: str
    status: ComponentStatusLiteral = "mandatory"
    reason: str
    supporting_decision_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class InterfaceItem(BaseModel):
    """Electrical, communication, and physical interface between components/subsystems (Section 11 & 12)."""

    interface_id: str
    source: str
    target: str
    interface_type: InterfaceTypeLiteral
    purpose: str
    direction: Literal["unidirectional", "bidirectional"] = "bidirectional"
    voltage_logic: Optional[str] = None
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class PowerDomainItem(BaseModel):
    """Power domain and voltage rail architecture (Section 14)."""

    power_domain_id: str
    name: str
    source: str
    voltage: str
    loads: List[str] = Field(default_factory=list)
    estimated_current: Optional[str] = None
    regulation: str
    protection: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_required: bool = True


class DataFlowItem(BaseModel):
    """Data pathway across sensors, compute, and actuators (Section 16)."""

    flow_id: str
    source: str
    destination: str
    data_type: str
    protocol: str
    direction: str = "unidirectional"
    latency_requirement: Optional[str] = None
    bandwidth_requirement: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)


class ControlFlowItem(BaseModel):
    """Control hierarchy and trigger flow (Section 17)."""

    control_id: str
    control_source: str
    control_target: str
    trigger: str
    decision_stage: str
    feedback_path: Optional[str] = None


class FeedbackLoopItem(BaseModel):
    """Closed-loop control and sensing feedback loop (Section 18)."""

    loop_id: str
    type: str = "closed_loop_control"
    sensor: str
    controller: str
    actuator: str
    feedback_signal: str
    validation_required: bool = True


class SoftwareLayerItem(BaseModel):
    """Software architecture stack layer (Section 19)."""

    layer_id: str
    name: str
    responsibilities: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class HardwareSoftwareBoundary(BaseModel):
    """Explicit division of responsibilities across system layers (Section 20)."""

    hardware_responsibilities: List[str] = Field(default_factory=list)
    firmware_responsibilities: List[str] = Field(default_factory=list)
    software_responsibilities: List[str] = Field(default_factory=list)
    ai_responsibilities: List[str] = Field(default_factory=list)
    cloud_responsibilities: List[str] = Field(default_factory=list)


class PhysicalArchitectureItem(BaseModel):
    """Physical layout, placement, and enclosure relationships (Section 21)."""

    element_id: str
    category: str  # enclosure, mounting, sensor_placement, compute_placement, battery_placement, pcb, connectors
    description: str
    constraints: List[str] = Field(default_factory=list)


class ThermalElementItem(BaseModel):
    """Thermal architecture and heat dissipation elements (Section 22)."""

    thermal_element_id: str
    source: str
    thermal_risk: str
    mitigation: str
    validation_required: bool = True


class DependencyItem(BaseModel):
    """Inter-component / inter-subsystem architectural dependency (Section 25)."""

    dependency_id: str
    source: str
    dependency_type: DependencyTypeLiteral
    target: str
    description: str
    mandatory: bool = True
    validation_required: bool = True


class ArchitectureDecision(BaseModel):
    """Core architectural decision item (Section 27)."""

    architecture_decision_id: str
    decision_area: str
    selected_architecture: str
    alternatives: List[str] = Field(default_factory=list)
    reason: str
    supporting_decision_ids: List[str] = Field(default_factory=list)
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_required: bool = True


class ArchitectureAlternative(BaseModel):
    """Evaluated alternative architecture design (Section 26)."""

    alternative_id: str
    name: str
    description: str
    tradeoff_analysis: Dict[str, Any] = Field(default_factory=dict)
    selected: bool = False


class ArchitectureRisk(BaseModel):
    """Architecture-level risk evaluation (Section 28)."""

    risk_id: str
    category: str
    description: str
    affected_subsystems: List[str] = Field(default_factory=list)
    likelihood: Literal["low", "medium", "high"] = "medium"
    impact: Literal["low", "medium", "high"] = "medium"
    mitigation: str
    validation_required: bool = True


class ArchitectureValidationRequirement(BaseModel):
    """Architecture-level verification and validation procedure (Section 29)."""

    validation_id: str
    category: str  # electrical, power, communication, thermal, software, mechanical
    description: str
    acceptance_criteria: str
    affected_subsystem_ids: List[str] = Field(default_factory=list)


class ArchitectureTraceability(BaseModel):
    """Full traceability chain from requirement to validation (Section 30)."""

    traceability_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    engineering_decision_ids: List[str] = Field(default_factory=list)
    architecture_decision_ids: List[str] = Field(default_factory=list)
    subsystem_ids: List[str] = Field(default_factory=list)
    component_ids: List[str] = Field(default_factory=list)
    interface_ids: List[str] = Field(default_factory=list)
    validation_ids: List[str] = Field(default_factory=list)


class DiagramNode(BaseModel):
    """Block diagram node (Section 31)."""

    id: str
    type: str
    label: str
    subsystem: Optional[str] = None


class DiagramEdge(BaseModel):
    """Block diagram edge (Section 31)."""

    source: str
    target: str
    type: str  # data, control, power, mechanical
    label: str


class BlockDiagram(BaseModel):
    """Machine-readable block diagram structure (Section 31)."""

    nodes: List[DiagramNode] = Field(default_factory=list)
    edges: List[DiagramEdge] = Field(default_factory=list)


class GraphNode(BaseModel):
    """Architecture graph node (Section 32)."""

    id: str
    type: str  # project, subsystem, component, interface, power_domain, software_module, data_flow, control_flow, requirement, decision, risk, validation
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Architecture graph edge (Section 32)."""

    source: str
    target: str
    relationship: str  # contains, connects_to, powered_by, communicates_with, controls, senses, depends_on, implements, satisfies, validated_by, constrained_by, derived_from


class ArchitectureGraph(BaseModel):
    """Graph-ready architectural model (Section 32)."""

    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


class ArchitectureMeta(BaseModel):
    """Top-level architecture metadata."""

    architecture_id: str = "ARCH-001"
    architecture_name: str
    description: str
    architecture_type: str
    confidence: float = Field(default=0.90, ge=0.0, le=1.0)


class ArchitectureComponentRequirement(BaseModel):
    """Component requirement specification passed downstream to Agent #7 (Section 35)."""

    category: str
    quantity: int = 1
    required_specs: List[str] = Field(default_factory=list)
    reason: str
    source_subsystem: str


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class EngineeringArchitectureAgentInput(BaseModel):
    """Structured input contract for EngineeringArchitectureAgent (Section 4)."""

    project: ProjectMeta
    engineering_synthesis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured synthesis report from Agent #5 (EngineeringSynthesisAgent).",
    )
    technical_findings: List[Dict[str, Any]] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    validation_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional directory to export the 8 required architecture artifacts.",
    )
    execution_context: Optional[RequestContext] = None


class EngineeringArchitectureAgentOutput(BaseModel):
    """Structured output contract for EngineeringArchitectureAgent (Section 33)."""

    status: Literal["success", "error"] = "success"
    project: ProjectMeta
    architecture: ArchitectureMeta
    subsystems: List[SubsystemItem] = Field(default_factory=list)
    component_roles: List[ComponentRoleItem] = Field(default_factory=list)
    interfaces: List[InterfaceItem] = Field(default_factory=list)
    power_domains: List[PowerDomainItem] = Field(default_factory=list)
    data_flows: List[DataFlowItem] = Field(default_factory=list)
    control_flows: List[ControlFlowItem] = Field(default_factory=list)
    feedback_loops: List[FeedbackLoopItem] = Field(default_factory=list)
    software_architecture: List[SoftwareLayerItem] = Field(default_factory=list)
    hardware_software_boundary: Optional[HardwareSoftwareBoundary] = None
    physical_architecture: List[PhysicalArchitectureItem] = Field(default_factory=list)
    thermal_architecture: List[ThermalElementItem] = Field(default_factory=list)
    communication_architecture: List[InterfaceItem] = Field(default_factory=list)
    dependencies: List[DependencyItem] = Field(default_factory=list)
    architecture_decisions: List[ArchitectureDecision] = Field(default_factory=list)
    alternatives: List[ArchitectureAlternative] = Field(default_factory=list)
    risks: List[ArchitectureRisk] = Field(default_factory=list)
    validation_requirements: List[ArchitectureValidationRequirement] = Field(default_factory=list)
    traceability: List[ArchitectureTraceability] = Field(default_factory=list)
    block_diagram: BlockDiagram = Field(default_factory=BlockDiagram)
    architecture_graph: ArchitectureGraph = Field(default_factory=ArchitectureGraph)
    component_requirements: List[ArchitectureComponentRequirement] = Field(default_factory=list)
    assumptions: List[Dict[str, Any]] = Field(default_factory=list)
    unknowns: List[Dict[str, Any]] = Field(default_factory=list)
    structured_report_markdown: str = ""
    warnings: List[str] = Field(default_factory=list)
    errors: List[StructuredError] = Field(default_factory=list)
