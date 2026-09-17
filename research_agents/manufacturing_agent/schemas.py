"""
Pydantic data contracts and schemas for Manufacturing / DFM-DFA Agent (Agent #24).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple
import uuid
from pydantic import BaseModel, Field

ProcessFamilyLiteral = Literal[
    "CNC_MACHINING",
    "TURNING",
    "MILLING",
    "DRILLING",
    "LASER_CUTTING",
    "WATERJET_CUTTING",
    "PLASMA_CUTTING",
    "SHEET_METAL_BENDING",
    "STAMPING",
    "CASTING",
    "INJECTION_MOLDING",
    "EXTRUSION",
    "FORGING",
    "WELDING",
    "BRAZING",
    "SOLDERING",
    "ADHESIVE_BONDING",
    "RIVETING",
    "FASTENING",
    "ADDITIVE_MANUFACTURING",
    "PCB_ASSEMBLY",
    "CABLE_HARNESS_ASSEMBLY",
    "COMPOSITE_MANUFACTURING",
    "MANUAL_ASSEMBLY",
    "AUTOMATED_ASSEMBLY",
]

VolumeTierLiteral = Literal[
    "PROTOTYPE",
    "LOW_VOLUME",
    "MEDIUM_VOLUME",
    "HIGH_VOLUME",
    "MASS_PRODUCTION",
]

EvidenceLevelLiteral = Literal["E0", "E1", "E2", "E3", "E4", "E5"]
FindingSeverityLiteral = Literal["BLOCKER", "CRITICAL", "MAJOR", "MINOR", "INFO"]
FindingStatusLiteral = Literal["OPEN", "UNDER_REVIEW", "MITIGATED", "ACCEPTED", "WAIVED"]
ReadinessVerdictLiteral = Literal[
    "NOT_ASSESSED",
    "DFM_BLOCKED",
    "DFA_BLOCKED",
    "CONDITIONAL",
    "PROTOTYPE_READY",
    "PILOT_READY",
    "PRODUCTION_READY",
    "REQUIRES_VALIDATION",
]
ToleranceClassificationLiteral = Literal[
    "FUNCTIONALLY_REQUIRED",
    "LIKELY_OVER_SPECIFIED",
    "MANUFACTURING_CONCERN",
    "INSPECTION_CONCERN",
    "UNRESOLVED",
]
VerificationStateLiteral = Literal["PROPOSED", "TEST_REQUIRED", "VERIFIED", "FAILED", "WAIVED"]


class ManufacturingProcess(BaseModel):
    """Evaluated or candidate manufacturing process (Section 3)."""

    process_id: str = Field(default_factory=lambda: f"PROC-{uuid.uuid4().hex[:6].upper()}")
    name: str
    family: ProcessFamilyLiteral = "CNC_MACHINING"
    geometric_compatibility: Literal["YES", "NO", "CONDITIONAL", "UNKNOWN"] = "YES"
    material_compatibility: Literal["YES", "NO", "CONDITIONAL", "UNKNOWN"] = "YES"
    tolerance_capability: Literal["STRONG", "ACCEPTABLE", "POOR", "UNKNOWN"] = "ACCEPTABLE"
    surface_finish_capability: Literal["STRONG", "ACCEPTABLE", "POOR", "UNKNOWN"] = "ACCEPTABLE"
    volume_suitability: Literal["STRONG", "ACCEPTABLE", "POOR", "UNKNOWN"] = "ACCEPTABLE"
    tooling_complexity: Literal["LOW", "MEDIUM", "HIGH", "UNKNOWN"] = "MEDIUM"
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL", "UNKNOWN"] = "LOW"
    evidence_level: EvidenceLevelLiteral = "E2"
    evidence_ref: Optional[str] = None
    notes: str = ""


class DFMFinding(BaseModel):
    """Design-for-Manufacturing finding / issue (Section 1.1)."""

    finding_id: str = Field(default_factory=lambda: f"DFM-{uuid.uuid4().hex[:6].upper()}")
    component_id: str
    feature_id: Optional[str] = None
    process_id: Optional[str] = None
    category: Literal[
        "FEATURE_ACCESSIBILITY",
        "TOLERANCE_DIFFICULTY",
        "WALL_THICKNESS",
        "TOOL_DEFLECTION",
        "DRAFT_ANGLE",
        "UNDERCUT",
        "THERMAL_WARPAGE",
        "SURFACE_FINISH",
        "MATERIAL_PROCESS_MISMATCH",
        "STOCK_SIZE_EXCEEDED",
        "INSPECTION_INACCESSIBLE",
        "OTHER",
    ] = "FEATURE_ACCESSIBILITY"
    severity: FindingSeverityLiteral = "MAJOR"
    description: str
    rationale: str = ""
    evidence_level: EvidenceLevelLiteral = "E1"
    evidence_ref: Optional[str] = None
    assumptions: List[str] = Field(default_factory=list)
    unknowns: List[str] = Field(default_factory=list)
    affected_requirements: List[str] = Field(default_factory=list)
    status: FindingStatusLiteral = "OPEN"


class DFAFinding(BaseModel):
    """Design-for-Assembly finding / issue (Section 2)."""

    finding_id: str = Field(default_factory=lambda: f"DFA-{uuid.uuid4().hex[:6].upper()}")
    assembly_id: str = "MAIN_ASSEMBLY"
    affected_component_ids: List[str] = Field(default_factory=list)
    category: Literal[
        "PART_COUNT",
        "FASTENER_COUNT",
        "INSERTION_ACCESS",
        "TOOL_CLEARANCE",
        "ORIENTATION_AMBIGUITY",
        "ALIGNMENT",
        "POKA_YOKE_OPPORTUNITY",
        "CABLE_ROUTING",
        "CONNECTOR_ACCESS",
        "DISASSEMBLY_REPAIR",
        "REPEATED_OPERATIONS",
        "OTHER",
    ] = "FASTENER_COUNT"
    severity: FindingSeverityLiteral = "MAJOR"
    description: str
    rationale: str = ""
    proposed_poka_yoke: Optional[str] = None
    evidence_level: EvidenceLevelLiteral = "E1"
    status: FindingStatusLiteral = "OPEN"


class DFAModel(BaseModel):
    """Overall assembly characteristics and metrics."""

    assembly_id: str = "MAIN_ASSEMBLY"
    total_part_count: int = 0
    total_fastener_count: int = 0
    unique_fastener_types: int = 0
    estimated_assembly_steps: int = 0
    poka_yoke_score: float = 8.0
    findings: List[DFAFinding] = Field(default_factory=list)


class ToleranceItem(BaseModel):
    """Individual dimensional or geometric tolerance evaluation (Section 4)."""

    tolerance_id: str = Field(default_factory=lambda: f"TOL-{uuid.uuid4().hex[:6].upper()}")
    component_id: str
    feature_name: str
    datum: Optional[str] = None
    nominal_value: float
    unit: str = "mm"
    upper_tol: float
    lower_tol: float
    normalized_span_mm: Optional[float] = None
    classification: ToleranceClassificationLiteral = "FUNCTIONALLY_REQUIRED"
    inspection_method: Optional[str] = None
    notes: str = ""


class VariationData(BaseModel):
    """Statistical process capability evaluation (Section 9)."""

    parameter_name: str
    usl: Optional[float] = None
    lsl: Optional[float] = None
    mean: Optional[float] = None
    std_dev: Optional[float] = None
    sample_size: int = 0
    cp: Optional[float] = None
    cpk: Optional[float] = None
    pp: Optional[float] = None
    ppk: Optional[float] = None
    is_sufficient: bool = False
    status: Literal["DATA_SUFFICIENT", "DATA_INSUFFICIENT"] = "DATA_INSUFFICIENT"
    missing_data_requirements: List[str] = Field(default_factory=list)


class ToolingRequirement(BaseModel):
    """Tooling and fixture requirement (Section 6)."""

    tooling_id: str = Field(default_factory=lambda: f"TOOL-{uuid.uuid4().hex[:6].upper()}")
    name: str
    type: Literal["JIG", "FIXTURE", "SOFT_JAWS", "DIE", "MOLD", "CUTTING_TOOL", "INSPECTION_FIXTURE", "CUSTOM"] = "FIXTURE"
    necessity: Literal["MANDATORY", "RECOMMENDED", "OPTIONAL"] = "MANDATORY"
    complexity: Literal["LOW", "MEDIUM", "HIGH", "SPECIALIZED"] = "MEDIUM"
    reuse_potential: Literal["STANDARD_CATALOG", "REUSABLE_MODULAR", "PROJECT_DEDICATED"] = "REUSABLE_MODULAR"
    associated_component_ids: List[str] = Field(default_factory=list)
    description: str = ""


class SequenceStep(BaseModel):
    """Single step in manufacturing or assembly sequence (Section 7)."""

    step_number: int
    operation_name: str
    process_type: str
    preceding_steps: List[int] = Field(default_factory=list)
    is_inspection_gate: bool = False
    duration_minutes: Optional[float] = None
    duration_status: Literal["KNOWN", "UNKNOWN"] = "UNKNOWN"
    notes: str = ""


class ProcessSequence(BaseModel):
    """Manufacturing process flow."""

    sequence_id: str = Field(default_factory=lambda: f"SEQ-{uuid.uuid4().hex[:6].upper()}")
    component_id: Optional[str] = None
    steps: List[SequenceStep] = Field(default_factory=list)


class InspectionItem(BaseModel):
    """Quality control and inspection requirement (Section 11)."""

    inspection_id: str = Field(default_factory=lambda: f"INSP-{uuid.uuid4().hex[:6].upper()}")
    component_id: str
    feature_or_characteristic: str
    inspection_type: Literal[
        "DIMENSIONAL",
        "VISUAL",
        "SURFACE_ROUGHNESS",
        "ELECTRICAL",
        "FUNCTIONAL",
        "LEAK_PRESSURE",
        "TORQUE_VERIFICATION",
        "WELD_NDT",
        "MATERIAL_VERIFICATION",
    ] = "DIMENSIONAL"
    measurement_method: str = "CMM / Caliper"
    accessibility: Literal["EASY", "RESTRICTED", "DIFFICULT", "UNKNOWN"] = "EASY"
    acceptance_criteria: str
    required_evidence: str = "Inspection Record Sheet"
    verification_status: VerificationStateLiteral = "PROPOSED"


class ManufacturingRecommendation(BaseModel):
    """Actionable DFM/DFA design improvement recommendation (Section 13)."""

    recommendation_id: str = Field(default_factory=lambda: f"REC-MFG-{uuid.uuid4().hex[:6].upper()}")
    finding_id: str
    component_id: str
    current_condition: str
    proposed_change: str
    engineering_rationale: str
    expected_manufacturing_impact: str
    expected_assembly_impact: str
    possible_engineering_tradeoffs: str
    confidence: float = 0.90
    evidence_level: EvidenceLevelLiteral = "E2"
    affected_requirements: List[str] = Field(default_factory=list)
    change_request_id: Optional[str] = None


class CostDriverHandoff(BaseModel):
    """Structured cost drivers exported for Agent #25 (Section 14)."""

    project_id: str
    component_id: str
    process_family: str
    part_count_impact: str
    setup_count_estimate: int = 1
    tooling_complexity: str = "MEDIUM"
    tolerance_difficulty: str = "STANDARD"
    inspection_burden: str = "STANDARD"
    material_scrap_driver: Optional[str] = None
    automation_potential: str = "HIGH"


class ManufacturingReadiness(BaseModel):
    """Structured manufacturing readiness assessment (Section 41)."""

    project_id: str
    verdict: ReadinessVerdictLiteral = "NOT_ASSESSED"
    dfm_score: float = 85.0
    dfa_score: float = 85.0
    composite_manufacturability_score: float = 85.0
    active_blockers: List[str] = Field(default_factory=list)
    unresolved_tolerances: List[str] = Field(default_factory=list)
    unverified_inspection_criteria: List[str] = Field(default_factory=list)
    confidence: float = 0.85
    summary: str = ""


class ManufacturingDashboardData(BaseModel):
    """Executive dashboard summary data (Section 43)."""

    project_id: str
    total_components_analyzed: int = 0
    total_dfm_findings: int = 0
    total_dfa_findings: int = 0
    blockers_count: int = 0
    recommendations_count: int = 0
    readiness_verdict: ReadinessVerdictLiteral = "PROTOTYPE_READY"
    dfm_score: float = 85.0
    dfa_score: float = 85.0


class ProcessCapabilityComparison(BaseModel):
    """Structured candidate process trade-off comparison (Section 3)."""

    candidate_process_a: ManufacturingProcess
    candidate_process_b: ManufacturingProcess
    comparison_summary: str
    recommended_process: Optional[str] = None
    tradeoffs: List[str] = Field(default_factory=list)


class ManufacturingAgentInput(BaseModel):
    """Input contract for Manufacturing / DFM-DFA Agent."""

    project_id: str
    team_id: str = "default_team"
    user_id: str = "user_001"
    operation: Literal[
        "full_analysis",
        "dfm_analysis",
        "dfa_analysis",
        "process_selection",
        "tolerance_analysis",
        "variation_analysis",
        "tooling_analysis",
        "sequence_analysis",
        "inspection_analysis",
        "readiness_assessment",
        "reassess_change",
        "export_artifacts",
    ] = "full_analysis"

    # Engineering contexts
    project: Optional[Dict[str, Any]] = None
    design: Optional[Dict[str, Any]] = None
    components: Optional[List[Dict[str, Any]]] = None
    assemblies: Optional[List[Dict[str, Any]]] = None
    tolerances: Optional[List[Dict[str, Any]]] = None
    processes: Optional[List[Dict[str, Any]]] = None
    materials: Optional[List[Dict[str, Any]]] = None
    variation_datasets: Optional[List[Dict[str, Any]]] = None
    volume_tier: VolumeTierLiteral = "PROTOTYPE"
    change_request: Optional[Dict[str, Any]] = None
    authorization: Optional[Dict[str, Any]] = None

    # Targeted entities
    component_id: Optional[str] = None
    process_id: Optional[str] = None
    output_dir: Optional[str] = None

    # Custom payload
    payload: Optional[Dict[str, Any]] = None


class ManufacturingAgentOutput(BaseModel):
    """Output contract for Manufacturing / DFM-DFA Agent."""

    agent_id: str = "Agent #24"
    agent_name: str = "ManufacturingDFMAgent"
    fabric_id: str = "agent.24"
    status: Literal["success", "blocked", "error", "authorization_denied", "access_denied"] = "success"
    project_id: str
    operation: str
    processes: List[ManufacturingProcess] = Field(default_factory=list)
    dfm_findings: List[DFMFinding] = Field(default_factory=list)
    dfa_models: List[DFAModel] = Field(default_factory=list)
    tolerances: List[ToleranceItem] = Field(default_factory=list)
    variations: List[VariationData] = Field(default_factory=list)
    tooling_requirements: List[ToolingRequirement] = Field(default_factory=list)
    sequences: List[ProcessSequence] = Field(default_factory=list)
    inspections: List[InspectionItem] = Field(default_factory=list)
    recommendations: List[ManufacturingRecommendation] = Field(default_factory=list)
    cost_drivers: List[CostDriverHandoff] = Field(default_factory=list)
    readiness: Optional[ManufacturingReadiness] = None
    dashboard: Optional[ManufacturingDashboardData] = None
    structured_markdown_report: str = ""
    error_message: Optional[str] = None
    execution_duration_seconds: float = 0.0
