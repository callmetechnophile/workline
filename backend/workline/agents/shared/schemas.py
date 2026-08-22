"""Pydantic schemas for structured outputs across all Workline ADK agents."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentFinding(BaseModel):
    category: str
    title: str
    detail: str
    severity: Optional[str] = "INFO"  # INFO, WARN, ERROR
    source: Optional[str] = None


class AgentOutput(BaseModel):
    """Universal structured output returned by all specialist agents."""
    agent: str
    status: str = "COMPLETED"  # COMPLETED, WAITING_FOR_USER, FAILED, BLOCKED
    stage: str
    summary: str
    findings: List[AgentFinding] = Field(default_factory=list)
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    requires_user_action: bool = False
    action_prompt: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Specialist Agent Output Payloads ---

class DomainOutput(BaseModel):
    problem_definition: str
    engineering_domain: str
    initial_requirements: List[str]
    operating_constraints: Dict[str, Any]
    unknowns: List[str]
    research_questions: List[str]


class TimelineMilestone(BaseModel):
    id: str
    name: str
    stage: str
    duration_days: int
    dependencies: List[str] = Field(default_factory=list)
    tasks: List[str] = Field(default_factory=list)


class TimelineOutput(BaseModel):
    task_graph: List[Dict[str, Any]]
    milestones: List[TimelineMilestone]
    estimated_duration_weeks: int
    critical_path: List[str]


class ResearchSource(BaseModel):
    title: str
    url_or_ref: str
    key_findings: List[str]
    relevance: str


class ResearchOutput(BaseModel):
    approaches: List[str]
    existing_solutions: List[str]
    papers: List[ResearchSource]
    design_patterns: List[str]
    component_insights: List[str]


class InnovationOutput(BaseModel):
    facts: List[str] = Field(default_factory=list)
    inferences: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    technology_gaps: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)


class CandidateComponent(BaseModel):
    category: str
    name: str
    part_number: Optional[str] = None
    vendor: Optional[str] = None
    description: str
    estimated_price_usd: Optional[float] = None
    specifications: Dict[str, Any] = Field(default_factory=dict)


class ComponentValidationItem(BaseModel):
    name: str
    status: str  # VALIDATED, WARNING, UNKNOWN, INCOMPATIBLE
    voltage_range: Optional[str] = "UNKNOWN"
    current_draw: Optional[str] = "UNKNOWN"
    interface: Optional[str] = "UNKNOWN"
    operating_temp: Optional[str] = "UNKNOWN"
    package: Optional[str] = "UNKNOWN"
    notes: str


class ConnectionSignal(BaseModel):
    source_component: str
    source_pin: str
    target_component: str
    target_pin: str
    signal_type: str  # I2C, SPI, UART, GPIO, POWER, GND
    bus_name: Optional[str] = None


class PowerRail(BaseModel):
    voltage_v: float
    max_current_ma: float
    components_powered: List[str]
    regulator_ic: Optional[str] = None


class PowerArchitecture(BaseModel):
    input_source: str
    rails: List[PowerRail]
    total_power_mw: float
    thermal_considerations: List[str]


class FirmwareTask(BaseModel):
    name: str
    priority: int
    rate_hz: float
    description: str


class FirmwareArchitecture(BaseModel):
    framework: str  # ESP-IDF, FreeRTOS, Arduino, Zephyr
    hal_drivers: List[str]
    tasks: List[FirmwareTask]
    communication_protocols: List[str]


class PCBConstraints(BaseModel):
    board_type: str
    layer_count: int
    placement_rules: List[str]
    routing_rules: List[str]
    thermal_constraints: List[str]
    signal_integrity_notes: List[str]
    physics_simulation_status: str = "NOT_IMPLEMENTED"


class ValidationCheck(BaseModel):
    stage: str
    component_or_subsystem: str
    status: str  # PASS, WARN, FAIL
    issue: Optional[str] = None
    evidence: Optional[str] = None
    severity: Optional[str] = None  # LOW, MEDIUM, HIGH, CRITICAL
    recommended_action: Optional[str] = None


class ValidationReport(BaseModel):
    overall_status: str  # PASS, WARN, FAIL
    checks: List[ValidationCheck]
    summary: str


class BOMItemModel(BaseModel):
    designator: str
    component_name: str
    quantity: int
    unit_cost_usd: float
    vendor: str
    validation_status: str
    notes: Optional[str] = None


class BOMOutput(BaseModel):
    project_name: str
    items: List[BOMItemModel]
    total_estimated_cost_usd: float
    item_count: int
