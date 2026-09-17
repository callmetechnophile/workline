"""
Pydantic data contracts and schemas for SecurityThreatModelingAgent (Agent #22).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
import uuid
from pydantic import BaseModel, Field

AssetTypeLiteral = Literal[
    "DATA",
    "SERVICE",
    "AGENT",
    "API",
    "MODEL",
    "CREDENTIAL",
    "DEVICE",
    "DATABASE",
    "ARTIFACT",
    "INFRASTRUCTURE",
]

AssetClassificationLiteral = Literal[
    "PUBLIC",
    "INTERNAL",
    "CONFIDENTIAL",
    "RESTRICTED",
    "CRITICAL",
]

AssetCategoryLiteral = Literal[
    "USER_DATA",
    "PROJECT_DATA",
    "TEAM_DATA",
    "ENGINEERING_ARTIFACTS",
    "SOURCE_CODE",
    "BOM",
    "REQUIREMENTS",
    "SIMULATION_DATA",
    "VERIFICATION_DATA",
    "COMPLIANCE_DATA",
    "GRAPH_DATA",
    "CREDENTIALS",
    "API_KEYS",
    "TOKENS",
    "AGENT_STATE",
    "MODEL_INPUTS",
    "MODEL_OUTPUTS",
    "A2A_MESSAGES",
    "EVENTS",
    "LOGS",
    "AUDIT_RECORDS",
    "CONFIGURATION",
    "HARDWARE",
    "FIRMWARE",
    "DEPLOYMENT_INFRASTRUCTURE",
    "EXTERNAL_CONNECTIONS",
]

ThreatActorTypeLiteral = Literal[
    "EXTERNAL",
    "INTERNAL",
    "COMPROMISED_USER",
    "COMPROMISED_AGENT",
    "MALICIOUS_SERVICE",
    "SUPPLY_CHAIN",
    "UNKNOWN",
]

SecurityZoneLiteral = Literal[
    "PUBLIC",
    "USER",
    "FRONTEND",
    "API",
    "CONTROL_FABRIC",
    "AGENT_RUNTIME",
    "PRIVILEGED_EXECUTION",
    "DATABASE",
    "EXTERNAL_SERVICE",
    "HARDWARE",
    "CI_CD",
    "ADMIN",
    "MONITORING",
]

EntryTypeLiteral = Literal[
    "API",
    "WEB",
    "CLI",
    "A2A",
    "FILE",
    "NETWORK",
    "AUTH",
    "TOOL",
    "PLUGIN",
    "DEVICE",
    "EXTERNAL_SERVICE",
]

ExposureLiteral = Literal["PUBLIC", "INTERNAL", "RESTRICTED"]

ThreatCategoryLiteral = Literal[
    "SPOOFING",
    "TAMPERING",
    "REPUDIATION",
    "INFORMATION_DISCLOSURE",
    "DENIAL_OF_SERVICE",
    "ELEVATION_OF_PRIVILEGE",
    "PROMPT_INJECTION",
    "AGENT_HIJACKING",
    "TOOL_ABUSE",
    "MODEL_ABUSE",
    "DATA_POISONING",
    "SUPPLY_CHAIN",
    "CREDENTIAL_THEFT",
    "SESSION_HIJACKING",
    "AUTHORIZATION_BYPASS",
    "TENANT_ISOLATION",
    "API_ABUSE",
    "A2A_ATTACK",
    "PLUGIN_ATTACK",
    "DEPENDENCY_ATTACK",
    "SECRETS_EXPOSURE",
    "MALICIOUS_FILE",
    "MALICIOUS_ARTIFACT",
    "CODE_EXECUTION",
    "REMOTE_EXECUTION",
    "NETWORK_ATTACK",
    "PHYSICAL_ATTACK",
    "INSIDER_THREAT",
    "OTHER",
]

ThreatStatusLiteral = Literal[
    "IDENTIFIED",
    "ASSESSED",
    "MITIGATING",
    "MONITORED",
    "ACCEPTED",
    "CLOSED",
    "INVALIDATED",
]

ControlCategoryLiteral = Literal[
    "AUTHENTICATION",
    "AUTHORIZATION",
    "INPUT_VALIDATION",
    "OUTPUT_VALIDATION",
    "ENCRYPTION",
    "SECRETS_MANAGEMENT",
    "NETWORK_SECURITY",
    "ISOLATION",
    "RATE_LIMITING",
    "MONITORING",
    "LOGGING",
    "AUDITING",
    "SANDBOXING",
    "LEAST_PRIVILEGE",
    "CONTENT_FILTERING",
    "PROMPT_GUARD",
    "TOOL_GUARD",
    "A2A_SECURITY",
    "DATA_LOSS_PREVENTION",
    "BACKUP",
    "RECOVERY",
    "SUPPLY_CHAIN_SECURITY",
    "CODE_SIGNING",
    "INTEGRITY_CHECKING",
]

MitigationPriorityLiteral = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
MitigationStatusLiteral = Literal["PROPOSED", "APPROVED", "IMPLEMENTED", "VERIFIED", "REJECTED"]
VerificationStatusLiteral = Literal["UNVERIFIED", "PARTIAL", "VERIFIED"]
SecurityGateLiteral = Literal["SECURITY_PASS", "SECURITY_REVIEW_REQUIRED", "SECURITY_BLOCKED"]
FindingStatusLiteral = Literal["OPEN", "FIXED", "VERIFIED", "ACCEPTED", "FALSE_POSITIVE"]


class AssetObject(BaseModel):
    """Protected system or project asset (Section 6)."""

    asset_id: str = Field(default_factory=lambda: f"ASSET-{uuid.uuid4().hex[:6].upper()}")
    project_id: str
    name: str
    type: AssetTypeLiteral = "DATA"
    category: AssetCategoryLiteral = "PROJECT_DATA"
    classification: AssetClassificationLiteral = "CONFIDENTIAL"
    owner: Optional[str] = None
    description: str = ""
    source: str = "ARCHITECTURE"


class ThreatActor(BaseModel):
    """Threat actor model (Section 8)."""

    actor_id: str = Field(default_factory=lambda: f"ACTOR-{uuid.uuid4().hex[:6].upper()}")
    name: str
    type: ThreatActorTypeLiteral = "EXTERNAL"
    capabilities: List[str] = Field(default_factory=list)
    access_level: str = "UNAUTHENTICATED"
    motivation: List[str] = Field(default_factory=list)
    description: str = ""


class TrustBoundary(BaseModel):
    """Logical or physical trust boundary crossing (Section 9)."""

    boundary_id: str = Field(default_factory=lambda: f"TB-{uuid.uuid4().hex[:6].upper()}")
    name: str
    source_zone: SecurityZoneLiteral
    destination_zone: SecurityZoneLiteral
    controls: List[str] = Field(default_factory=list)
    data_types: List[str] = Field(default_factory=list)
    description: str = ""


class AttackSurfaceEntry(BaseModel):
    """Exposed system entry point (Section 11)."""

    entry_id: str = Field(default_factory=lambda: f"ENTRY-{uuid.uuid4().hex[:6].upper()}")
    asset_id: Optional[str] = None
    type: EntryTypeLiteral = "API"
    protocol: Optional[str] = "HTTPS / JSON"
    authentication: Optional[str] = "JWT / Bearer Token"
    authorization: Optional[str] = "ArmorIQ Scope Check"
    exposure: ExposureLiteral = "PUBLIC"
    endpoint_path: Optional[str] = None
    description: str = ""


class SecurityDataFlow(BaseModel):
    """Sensitive data flow crossing trust boundaries (Section 13)."""

    flow_id: str = Field(default_factory=lambda: f"FLOW-{uuid.uuid4().hex[:6].upper()}")
    source: str
    destination: str
    data_type: str
    protocol: str = "HTTPS"
    trust_boundary_crossed: bool = True
    authentication: str = "Bearer Token"
    authorization: str = "Scope Verified"
    encryption: str = "TLS 1.3"
    validation: str = "Pydantic Schema Validation"
    logging: str = "Sanitized Structured Log"


class AttackPath(BaseModel):
    """Exploitable sequence of steps across trust boundaries (Section 43)."""

    attack_path_id: str = Field(default_factory=lambda: f"PATH-{uuid.uuid4().hex[:6].upper()}")
    threat_id: str
    steps: List[str] = Field(default_factory=list)
    entry_point: str = "Public API"
    target_asset: str = "Project Database"
    required_privileges: List[str] = Field(default_factory=list)
    controls_crossed: List[str] = Field(default_factory=list)
    likelihood: Optional[int] = None
    impact: Optional[int] = None


class SecurityControl(BaseModel):
    """Safeguard or mitigation countermeasure (Section 45)."""

    control_id: str = Field(default_factory=lambda: f"CTRL-{uuid.uuid4().hex[:6].upper()}")
    name: str
    category: ControlCategoryLiteral = "AUTHORIZATION"
    description: str = ""
    implemented: bool = True
    implementation_reference: Optional[str] = None
    verification_status: VerificationStatusLiteral = "UNVERIFIED"
    evidence_ids: List[str] = Field(default_factory=list)


class ThreatMitigation(BaseModel):
    """Actionable security mitigation item (Section 47)."""

    mitigation_id: str = Field(default_factory=lambda: f"SEC-MIT-{uuid.uuid4().hex[:6].upper()}")
    threat_id: str
    control_id: Optional[str] = None
    action: str
    priority: MitigationPriorityLiteral = "MEDIUM"
    owner: Optional[str] = None
    status: MitigationStatusLiteral = "PROPOSED"
    change_request_id: Optional[str] = None
    verification_id: Optional[str] = None


class SecurityTestCase(BaseModel):
    """Executable security test specification for Agent #18 (Section 79)."""

    security_test_id: str = Field(default_factory=lambda: f"SEC-TEST-{uuid.uuid4().hex[:6].upper()}")
    threat_id: str
    objective: str
    test_type: str = "AUTHORIZATION"
    preconditions: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    expected_result: str
    severity: MitigationPriorityLiteral = "HIGH"
    verification_status: Literal["NOT_RUN", "PASS", "FAIL", "BLOCKED"] = "NOT_RUN"


class SecurityFinding(BaseModel):
    """Specific security vulnerability or misconfiguration finding (Section 53)."""

    finding_id: str = Field(default_factory=lambda: f"FIND-{uuid.uuid4().hex[:6].upper()}")
    threat_id: str
    severity: MitigationPriorityLiteral = "MEDIUM"
    description: str
    evidence_ids: List[str] = Field(default_factory=list)
    affected_assets: List[str] = Field(default_factory=list)
    recommendation: str = ""
    status: FindingStatusLiteral = "OPEN"
    false_positive_reason: Optional[str] = None


class ThreatObject(BaseModel):
    """Core Threat Model entity (Section 14)."""

    threat_id: str = Field(default_factory=lambda: f"THREAT-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: str = "default_team"
    user_id: str = "user_001"
    title: str
    description: str = ""
    category: ThreatCategoryLiteral = "INFORMATION_DISCLOSURE"
    asset_ids: List[str] = Field(default_factory=list)
    entry_point_ids: List[str] = Field(default_factory=list)
    actor_ids: List[str] = Field(default_factory=list)
    attack_path_ids: List[str] = Field(default_factory=list)
    severity: Optional[int] = 3
    likelihood: Optional[int] = 3
    risk_score: Optional[int] = 9
    status: ThreatStatusLiteral = "IDENTIFIED"
    mitigation_ids: List[str] = Field(default_factory=list)
    verification_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    is_critical: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class SecurityDashboardData(BaseModel):
    """Aggregated security dashboard posture (Section 74)."""

    project_id: str
    total_threats: int = 0
    critical_threats: int = 0
    high_threats: int = 0
    medium_threats: int = 0
    low_threats: int = 0
    open_findings: int = 0
    verified_controls: int = 0
    unverified_controls: int = 0
    public_attack_surfaces: int = 0
    privileged_attack_surfaces: int = 0
    cross_tenant_risks: int = 0
    credential_risks: int = 0
    prompt_injection_risks: int = 0
    a2a_risks: int = 0
    supply_chain_risks: int = 0
    security_score: float = 85.0
    security_gate: SecurityGateLiteral = "SECURITY_PASS"


class SecurityRiskProfile(BaseModel):
    """Configurable risk scoring profile (Section 50)."""

    profile_id: str = Field(default_factory=lambda: f"SEC-PROF-{uuid.uuid4().hex[:6].upper()}")
    name: str = "WorkflowGuide AI Security Risk Profile"
    likelihood_scale: Dict[int, str] = Field(default_factory=dict)
    impact_scale: Dict[int, str] = Field(default_factory=dict)
    risk_thresholds: Dict[str, int] = Field(default_factory=dict)
    version: str = "1.0.0"


class ChangeSecurityImpact(BaseModel):
    """Security impact of an engineering or architecture change (Section 57)."""

    change_id: str
    project_id: str
    affected_threat_ids: List[str] = Field(default_factory=list)
    affected_control_ids: List[str] = Field(default_factory=list)
    new_attack_surfaces: List[AttackSurfaceEntry] = Field(default_factory=list)
    new_attack_paths: List[AttackPath] = Field(default_factory=list)
    required_verification_ids: List[str] = Field(default_factory=list)
    is_regression: bool = False
    regression_details: List[str] = Field(default_factory=list)
    summary: str = ""


class SecurityThreatModelingAgentInput(BaseModel):
    """Input payload for SecurityThreatModelingAgent."""

    project_id: str
    team_id: str = "default_team"
    user_id: str = "user_001"
    operation: Literal[
        "full_threat_model",
        "discover_assets",
        "map_attack_surface",
        "model_threats",
        "assess_threat",
        "map_controls",
        "propose_mitigations",
        "verify_control",
        "generate_security_tests",
        "evaluate_security_gate",
        "get_change_security_impact",
        "reassess_security",
        "accept_threat",
        "export_artifacts",
    ] = "full_threat_model"

    # Context inputs
    project: Optional[Dict[str, Any]] = None
    architecture: Optional[Dict[str, Any]] = None
    agents_topology: Optional[List[Dict[str, Any]]] = None
    api_definitions: Optional[List[Dict[str, Any]]] = None
    dependencies: Optional[List[Dict[str, Any]]] = None
    verification_evidence: Optional[List[Dict[str, Any]]] = None
    change_request: Optional[Dict[str, Any]] = None
    authorization: Optional[Dict[str, Any]] = None
    security_incident: Optional[Dict[str, Any]] = None

    # Targeted entity IDs
    threat_id: Optional[str] = None
    asset_id: Optional[str] = None
    control_id: Optional[str] = None
    change_id: Optional[str] = None
    output_dir: Optional[str] = None

    # Custom payload
    payload: Optional[Dict[str, Any]] = None


class SecurityThreatModelingAgentOutput(BaseModel):
    """Output contract for SecurityThreatModelingAgent."""

    agent_id: str = "Agent #22"
    agent_name: str = "SecurityThreatModelingAgent"
    status: Literal["success", "blocked", "error", "authorization_denied", "access_denied"] = "success"
    project_id: str
    operation: str
    assets: List[AssetObject] = Field(default_factory=list)
    threat_actors: List[ThreatActor] = Field(default_factory=list)
    trust_boundaries: List[TrustBoundary] = Field(default_factory=list)
    attack_surface: List[AttackSurfaceEntry] = Field(default_factory=list)
    threats: List[ThreatObject] = Field(default_factory=list)
    attack_paths: List[AttackPath] = Field(default_factory=list)
    security_controls: List[SecurityControl] = Field(default_factory=list)
    mitigations: List[ThreatMitigation] = Field(default_factory=list)
    security_tests: List[SecurityTestCase] = Field(default_factory=list)
    findings: List[SecurityFinding] = Field(default_factory=list)
    dashboard: Optional[SecurityDashboardData] = None
    change_impact: Optional[ChangeSecurityImpact] = None
    structured_markdown_report: str = ""
    error_message: Optional[str] = None
    execution_duration_seconds: float = 0.0
