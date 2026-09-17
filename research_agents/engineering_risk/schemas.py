"""
Pydantic data contracts and schemas for EngineeringRiskAgent (Agent #21).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
import uuid
from pydantic import BaseModel, Field

RiskCategoryLiteral = Literal[
    "SAFETY",
    "FUNCTIONAL",
    "PERFORMANCE",
    "ELECTRICAL",
    "ELECTRONICS",
    "POWER",
    "THERMAL",
    "MECHANICAL",
    "SOFTWARE",
    "FIRMWARE",
    "AI_ML",
    "COMMUNICATION",
    "NETWORK",
    "SECURITY",
    "RELIABILITY",
    "MANUFACTURING",
    "SUPPLY_CHAIN",
    "ENVIRONMENTAL",
    "COMPLIANCE",
    "OPERATIONAL",
    "MAINTENANCE",
    "COST",
    "SCHEDULE",
    "INTEGRATION",
    "HUMAN_FACTORS",
    "OTHER",
]

RiskStatusLiteral = Literal[
    "IDENTIFIED",
    "ASSESSED",
    "OPEN",
    "MITIGATING",
    "MONITORED",
    "ACCEPTED",
    "CLOSED",
    "INVALIDATED",
    "REOPENED",
]

RiskLevelLiteral = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

CauseCategoryLiteral = Literal[
    "DESIGN",
    "COMPONENT",
    "MANUFACTURING",
    "SOFTWARE",
    "FIRMWARE",
    "CONFIGURATION",
    "ENVIRONMENT",
    "HUMAN",
    "INTERFACE",
    "SUPPLY_CHAIN",
    "MAINTENANCE",
    "UNKNOWN",
]

CauseEvidenceLiteral = Literal["CONFIRMED", "SUPPORTED", "HYPOTHESIS", "UNKNOWN", "USER_PROVIDED", "UNVERIFIED"]

MitigationTypeLiteral = Literal["PREVENTIVE", "DETECTIVE", "CORRECTIVE", "COMPENSATING"]

MitigationStatusLiteral = Literal["PROPOSED", "APPROVED", "IMPLEMENTED", "VERIFIED", "REJECTED"]

ConfidenceLiteral = Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]

DataQualityLiteral = Literal["COMPLETE", "PARTIAL", "INSUFFICIENT_DATA", "REVIEW_REQUIRED"]


class CauseObject(BaseModel):
    """Failure cause descriptor (Sections 21–22)."""

    cause_id: str = Field(default_factory=lambda: f"CAUSE-{uuid.uuid4().hex[:6].upper()}")
    description: str
    category: CauseCategoryLiteral = "DESIGN"
    evidence_status: CauseEvidenceLiteral = "HYPOTHESIS"
    evidence_source: Optional[str] = None
    notes: Optional[str] = None


class EffectObject(BaseModel):
    """Failure effect across abstraction hierarchy (Section 23)."""

    local_effect: str = ""
    subsystem_effect: str = ""
    system_effect: str = ""
    end_effect: str = ""


class ControlObject(BaseModel):
    """Current engineering control or safeguard in place."""

    control_id: str = Field(default_factory=lambda: f"CTRL-{uuid.uuid4().hex[:6].upper()}")
    description: str
    control_type: Literal["PREVENTION", "DETECTION"] = "DETECTION"
    implemented: bool = True
    detection_method: Optional[str] = None


class FailureMode(BaseModel):
    """Failure Mode representation (Section 8)."""

    failure_mode_id: str = Field(default_factory=lambda: f"FM-{uuid.uuid4().hex[:8].upper()}")
    risk_id: Optional[str] = None
    component_id: Optional[str] = None
    subsystem_id: Optional[str] = None
    interface_id: Optional[str] = None
    description: str
    failure_type: str = "FUNCTIONAL_FAILURE"
    local_effect: str = ""
    system_effect: str = ""
    end_effect: str = ""
    effects: Optional[EffectObject] = None
    causes: List[CauseObject] = Field(default_factory=list)
    controls: List[ControlObject] = Field(default_factory=list)
    detection_methods: List[str] = Field(default_factory=list)
    is_single_point_failure: bool = False
    redundancy_present: bool = False


class FMEARecord(BaseModel):
    """Failure Mode and Effects Analysis (FMEA) record (Sections 9–10)."""

    fmea_id: str = Field(default_factory=lambda: f"FMEA-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    failure_mode_id: str
    severity: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None
    risk_priority_number: Optional[int] = None
    occurrence_nature: Literal["ACTUAL_DATA", "ESTIMATED", "UNKNOWN"] = "ESTIMATED"
    occurrence_justification: Optional[str] = None
    current_controls: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    residual_severity: Optional[int] = None
    residual_occurrence: Optional[int] = None
    residual_detection: Optional[int] = None
    residual_rpn: Optional[int] = None
    status: Literal["OPEN", "MITIGATING", "REVIEW", "CLOSED"] = "OPEN"
    critical_review_required: bool = False
    critical_review_reason: Optional[str] = None


class RatingProfile(BaseModel):
    """Configurable rating scales profile (Section 12)."""

    rating_profile_id: str = Field(default_factory=lambda: f"RP-{uuid.uuid4().hex[:6].upper()}")
    name: str = "Standard Engineering Rating Profile"
    severity_scale: Dict[int, str] = Field(default_factory=dict)
    occurrence_scale: Dict[int, str] = Field(default_factory=dict)
    detection_scale: Dict[int, str] = Field(default_factory=dict)
    risk_thresholds: Dict[str, int] = Field(default_factory=dict)
    source: str = "WorkflowGuide AI Engineering Standards"
    version: str = "1.0.0"


class RiskMatrixProfile(BaseModel):
    """Configurable Likelihood x Consequence risk matrix (Section 20)."""

    risk_matrix_id: str = Field(default_factory=lambda: f"RM-{uuid.uuid4().hex[:6].upper()}")
    likelihood_levels: Dict[str, List[int]] = Field(default_factory=dict)
    severity_levels: Dict[str, List[int]] = Field(default_factory=dict)
    risk_bands: Dict[str, str] = Field(default_factory=dict)
    source: str = "WorkflowGuide AI Matrix Standard"
    version: str = "1.0.0"


class FaultPropagationObject(BaseModel):
    """Fault propagation path and cascading analysis (Section 25)."""

    propagation_id: str = Field(default_factory=lambda: f"PROP-{uuid.uuid4().hex[:8].upper()}")
    failure_mode_id: str
    path: List[str] = Field(default_factory=list)
    affected_nodes: List[str] = Field(default_factory=list)
    affected_requirements: List[str] = Field(default_factory=list)
    affected_functions: List[str] = Field(default_factory=list)
    severity: Optional[int] = None
    is_cascading: bool = False
    is_single_point_failure: bool = False
    common_cause_elements: List[str] = Field(default_factory=list)


class RiskMitigation(BaseModel):
    """Action item reducing occurrence, severity, or detection difficulty (Sections 30–31)."""

    mitigation_id: str = Field(default_factory=lambda: f"MIT-{uuid.uuid4().hex[:8].upper()}")
    risk_id: str
    action: str
    type: MitigationTypeLiteral = "PREVENTIVE"
    priority: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = "MEDIUM"
    owner: Optional[str] = None
    status: MitigationStatusLiteral = "PROPOSED"
    verification_id: Optional[str] = None
    verification_evidence_ref: Optional[str] = None
    change_request_id: Optional[str] = None
    target_reduction: Dict[str, int] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RiskObject(BaseModel):
    """Core Engineering Risk Object (Section 6)."""

    risk_id: str = Field(default_factory=lambda: f"RISK-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: str = "default_team"
    user_id: str = "user_001"
    title: str
    description: str = ""
    category: RiskCategoryLiteral = "FUNCTIONAL"
    source: str = "ENGINEERING_ANALYSIS"
    severity: Optional[int] = None
    likelihood: Optional[int] = None
    detectability: Optional[int] = None
    risk_score: Optional[int] = None
    risk_level: RiskLevelLiteral = "LOW"
    status: RiskStatusLiteral = "IDENTIFIED"
    confidence: ConfidenceLiteral = "MEDIUM"
    data_quality: DataQualityLiteral = "PARTIAL"
    mitigation_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    requirement_ids: List[str] = Field(default_factory=list)
    artifact_ids: List[str] = Field(default_factory=list)
    failure_mode_ids: List[str] = Field(default_factory=list)
    is_single_point_failure: bool = False
    critical_review_required: bool = False
    reopened_from_risk_id: Optional[str] = None
    invalidated_reason: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RiskDashboardData(BaseModel):
    """Aggregated risk summary metrics (Sections 57–59)."""

    project_id: str
    total_risks: int = 0
    open_risks: int = 0
    critical_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    mitigating_risks: int = 0
    accepted_risks: int = 0
    closed_risks: int = 0
    invalidated_risks: int = 0
    reopened_risks: int = 0
    unverified_mitigations: int = 0
    single_point_failures: int = 0
    average_rpn: float = 0.0
    high_risk_components: List[str] = Field(default_factory=list)
    risk_burndown_status: str = "INSUFFICIENT_HISTORY"


class ChangeRiskImpact(BaseModel):
    """Impact analysis on risks and failure modes resulting from an engineering change (Sections 41–42)."""

    change_id: str
    project_id: str
    affected_risk_ids: List[str] = Field(default_factory=list)
    affected_failure_mode_ids: List[str] = Field(default_factory=list)
    invalidated_mitigation_ids: List[str] = Field(default_factory=list)
    new_failure_modes_identified: List[FailureMode] = Field(default_factory=list)
    reassessed_fmea_records: List[FMEARecord] = Field(default_factory=list)
    verification_required_ids: List[str] = Field(default_factory=list)
    summary: str = ""


class RiskReassessmentPlan(BaseModel):
    """Action plan following design changes to restore risk baseline."""

    plan_id: str = Field(default_factory=lambda: f"RP-{uuid.uuid4().hex[:6].upper()}")
    change_id: str
    project_id: str
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    required_verifications: List[str] = Field(default_factory=list)


class EngineeringRiskAgentInput(BaseModel):
    """Input payload for EngineeringRiskAgent."""

    project_id: str
    team_id: str = "default_team"
    user_id: str = "user_001"
    operation: Literal[
        "full_analysis",
        "create_risk",
        "assess_risk",
        "create_fmea",
        "analyze_failure_mode",
        "analyze_fault_propagation",
        "identify_single_point_failures",
        "create_mitigation",
        "verify_mitigation",
        "assess_residual_risk",
        "get_risk_register",
        "get_fmea",
        "get_risk_dashboard",
        "get_risk_impact",
        "reassess_risk",
        "invalidate_risk",
        "accept_risk",
        "close_risk",
        "reopen_risk",
        "export_artifacts",
    ] = "full_analysis"

    # Context inputs
    project: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    bom: Optional[Dict[str, Any]] = None
    requirements: Optional[List[Dict[str, Any]]] = None
    interfaces: Optional[List[Dict[str, Any]]] = None
    verification_evidence: Optional[List[Dict[str, Any]]] = None
    compliance_findings: Optional[List[Dict[str, Any]]] = None
    simulation_results: Optional[List[Dict[str, Any]]] = None
    change_request: Optional[Dict[str, Any]] = None
    authorization: Optional[Dict[str, Any]] = None

    # Targeted entity IDs
    risk_id: Optional[str] = None
    failure_mode_id: Optional[str] = None
    component_id: Optional[str] = None
    subsystem_id: Optional[str] = None
    mitigation_id: Optional[str] = None
    change_id: Optional[str] = None
    output_dir: Optional[str] = None

    # Custom payload
    payload: Optional[Dict[str, Any]] = None


class EngineeringRiskAgentOutput(BaseModel):
    """Output contract for EngineeringRiskAgent."""

    agent_id: str = "Agent #21"
    agent_name: str = "EngineeringRiskAgent"
    status: Literal["success", "blocked", "error", "authorization_denied", "access_denied"] = "success"
    project_id: str
    operation: str
    risks: List[RiskObject] = Field(default_factory=list)
    failure_modes: List[FailureMode] = Field(default_factory=list)
    fmea_records: List[FMEARecord] = Field(default_factory=list)
    mitigations: List[RiskMitigation] = Field(default_factory=list)
    propagation_paths: List[FaultPropagationObject] = Field(default_factory=list)
    dashboard: Optional[RiskDashboardData] = None
    change_impact: Optional[ChangeRiskImpact] = None
    structured_markdown_report: str = ""
    error_message: Optional[str] = None
    execution_duration_seconds: float = 0.0
