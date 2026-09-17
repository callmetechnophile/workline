"""
Pydantic schemas and domain models for Agent #26 (DeploymentOpsAgent).
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SystemType(str, Enum):
    PHYSICAL = "PHYSICAL"
    SOFTWARE = "SOFTWARE"
    AI_AGENT = "AI_AGENT"
    CYBER_PHYSICAL = "CYBER_PHYSICAL"
    HYBRID = "HYBRID"


class DeploymentStage(str, Enum):
    DESIGN_READY = "DESIGN_READY"
    MANUFACTURING_READY = "MANUFACTURING_READY"
    PROCUREMENT_READY = "PROCUREMENT_READY"
    INSTALLATION_READY = "INSTALLATION_READY"
    CONFIGURATION_READY = "CONFIGURATION_READY"
    COMMISSIONING = "COMMISSIONING"
    VALIDATION = "VALIDATION"
    OPERATIONAL = "OPERATIONAL"
    MAINTENANCE = "MAINTENANCE"
    DECOMMISSIONING = "DECOMMISSIONING"


class ReadinessStatus(str, Enum):
    READY = "READY"
    CONDITIONAL = "CONDITIONAL"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    NOT_ASSESSED = "NOT_ASSESSED"


class CommissioningStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCKED = "BLOCKED"
    INCONCLUSIVE = "INCONCLUSIVE"
    WAIVED = "WAIVED"


class AlertSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class IncidentState(str, Enum):
    DETECTED = "DETECTED"
    TRIAGED = "TRIAGED"
    CONTAINED = "CONTAINED"
    RECOVERING = "RECOVERING"
    RECOVERED = "RECOVERED"
    CLOSED = "CLOSED"
    REVIEWED = "REVIEWED"


class ServiceabilityRating(str, Enum):
    SERVICEABILITY_ACCEPTABLE = "SERVICEABILITY_ACCEPTABLE"
    SERVICEABILITY_CONCERN = "SERVICEABILITY_CONCERN"
    SERVICEABILITY_BLOCKER = "SERVICEABILITY_BLOCKER"


class MaintenanceType(str, Enum):
    PREVENTIVE = "PREVENTIVE"
    CORRECTIVE = "CORRECTIVE"
    PREDICTIVE = "PREDICTIVE"
    CONDITION_BASED = "CONDITION_BASED"


class OperationalMode(str, Enum):
    NORMAL = "NORMAL"
    STARTUP = "STARTUP"
    SHUTDOWN = "SHUTDOWN"
    MAINTENANCE = "MAINTENANCE"
    DEGRADED = "DEGRADED"
    EMERGENCY = "EMERGENCY"
    RECOVERY = "RECOVERY"
    COMMISSIONING = "COMMISSIONING"
    DIAGNOSTIC = "DIAGNOSTIC"


# --- Sub-models ---

class DeploymentReadinessCriteria(BaseModel):
    criterion_id: str
    name: str
    category: str  # DESIGN, MANUFACTURING, INFRASTRUCTURE, POWER, SAFETY, COMPLIANCE, DOCS
    status: ReadinessStatus = ReadinessStatus.NOT_ASSESSED
    is_blocking: bool = False
    blocking_reason: Optional[str] = None
    notes: Optional[str] = None


class DeploymentStep(BaseModel):
    step_number: int
    title: str
    prerequisites: List[str] = Field(default_factory=list)
    action: str
    responsible_role: str = "DEVOPS_OR_FIELD_ENGINEER"
    required_tools: List[str] = Field(default_factory=list)
    required_materials: List[str] = Field(default_factory=list)
    expected_result: str
    verification_method: str
    rollback_action: Optional[str] = None
    requires_authorization: bool = False


class DeploymentPlan(BaseModel):
    plan_id: str
    project_id: str
    system_id: str
    system_type: SystemType = SystemType.HYBRID
    target_environment: str = "production"
    steps: List[DeploymentStep] = Field(default_factory=list)
    estimated_duration_minutes: Optional[float] = None
    blockers: List[str] = Field(default_factory=list)


class InstallationRequirement(BaseModel):
    req_id: str
    category: str  # LOCATION, MOUNTING, POWER, COOLING, RUNTIME, GPU, NETWORK
    description: str
    specification: str
    verified: bool = False


class CommissioningTest(BaseModel):
    test_id: str
    name: str
    subsystem: str
    expected_result: str
    actual_result: Optional[str] = None
    status: CommissioningStatus = CommissioningStatus.NOT_RUN
    evidence_reference: Optional[str] = None


class CommissioningPlan(BaseModel):
    plan_id: str
    project_id: str
    tests: List[CommissioningTest] = Field(default_factory=list)
    overall_status: CommissioningStatus = CommissioningStatus.NOT_RUN


class ConfigurationItem(BaseModel):
    item_id: str
    key: str
    value: str
    version: str = "1.0.0"
    environment: str = "production"
    is_secret: bool = False
    authorized_by: Optional[str] = None


class OperationalBaseline(BaseModel):
    baseline_id: str
    project_id: str
    system_id: str
    version: str = "1.0.0"
    timestamp: str = ""
    configurations: List[ConfigurationItem] = Field(default_factory=list)
    approved_operating_modes: List[OperationalMode] = Field(default_factory=list)
    is_active: bool = True


class EnvironmentRequirement(BaseModel):
    resource: str
    required_value: str
    actual_value: Optional[str] = None
    is_satisfied: bool = False


class OperationalDependency(BaseModel):
    dep_id: str
    system_id: str
    target_service_or_component: str
    dependency_type: str  # DATABASE, INFERENCE, FABRIC, POWER, SUBSYSTEM
    is_critical: bool = True
    is_single_point_of_failure: bool = False
    fallback_available: bool = False


class HealthMetric(BaseModel):
    metric_name: str
    current_value: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    unit: str = ""
    status: str = "HEALTHY"


class AlertRule(BaseModel):
    rule_id: str
    name: str
    condition: str
    severity: AlertSeverity
    affected_component: str
    response_procedure: str
    escalation: str


class IncidentRecord(BaseModel):
    incident_id: str
    project_id: str
    system_id: str
    symptoms: str
    severity: AlertSeverity
    state: IncidentState = IncidentState.DETECTED
    detection_source: str = "MONITORING"
    root_cause_type: str = "ROOT_CAUSE_HYPOTHESIS"  # ROOT_CAUSE_CONFIRMED or ROOT_CAUSE_HYPOTHESIS
    root_cause_description: Optional[str] = None
    recovery_action: Optional[str] = None
    evidence_reference: Optional[str] = None


class TroubleshootingNode(BaseModel):
    symptom: str
    possible_causes: List[str] = Field(default_factory=list)
    diagnostic_test: str = ""
    expected_result: str = ""
    next_action: str = ""


class TroubleshootingTree(BaseModel):
    tree_id: str
    system_id: str
    nodes: List[TroubleshootingNode] = Field(default_factory=list)


class RecoveryAction(BaseModel):
    action_id: str
    trigger: str
    strategy: str  # RESTART, ROLLBACK, FAILOVER, ISOLATION, RESTORE, DEGRADED
    prerequisites: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    verification: str = ""
    requires_authorization: bool = True


class RollbackPlan(BaseModel):
    plan_id: str
    system_id: str
    current_version: str
    target_version: str
    rollback_trigger: str
    steps: List[str] = Field(default_factory=list)
    is_destructive: bool = False
    requires_authorization: bool = True


class BackupRestorePlan(BaseModel):
    plan_id: str
    system_id: str
    backup_target: str
    frequency: str
    retention: str
    restore_procedure: str
    verification_procedure: str


class MaintenanceTask(BaseModel):
    task_id: str
    component_id: str
    maintenance_type: MaintenanceType
    action: str
    interval: str = "MAINTENANCE_INTERVAL_UNKNOWN"
    required_tools: List[str] = Field(default_factory=list)
    required_spares: List[str] = Field(default_factory=list)
    skill_level: str = "TECHNICIAN"
    safety_prerequisite: str = "SAFETY_INFORMATION_REQUIRED"


class ServiceabilityEvaluation(BaseModel):
    subsystem_id: str
    rating: ServiceabilityRating
    access_notes: str
    replaceability_notes: str
    concerns: List[str] = Field(default_factory=list)


class SparePartRequirement(BaseModel):
    part_id: str
    part_name: str
    recommended_stock_qty: int = 1
    lead_time_weeks: Optional[float] = None
    is_single_source: bool = False
    is_critical: bool = True
    sourcing_risk_level: str = "LOW"


class DecommissioningPlan(BaseModel):
    plan_id: str
    project_id: str
    system_id: str
    shutdown_sequence: List[str] = Field(default_factory=list)
    data_preservation_steps: List[str] = Field(default_factory=list)
    credential_revocation_steps: List[str] = Field(default_factory=list)
    asset_disposition_steps: List[str] = Field(default_factory=list)


# --- Input / Output Contracts ---

class DeploymentOpsInput(BaseModel):
    project_id: str
    system_id: str = "SYS-PRIMARY"
    system_type: SystemType = SystemType.HYBRID
    operation: str = "full_analysis"  # readiness, plan, commissioning, monitoring, maintenance, recovery, decommission, full_analysis
    team_id: Optional[str] = None
    user_id: Optional[str] = None
    environment: str = "production"
    components: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[OperationalDependency] = Field(default_factory=list)
    configurations: List[ConfigurationItem] = Field(default_factory=list)
    known_risks: List[Dict[str, Any]] = Field(default_factory=list)
    dfm_handoff: Optional[Dict[str, Any]] = None
    reliability_handoff: Optional[Dict[str, Any]] = None
    supply_chain_handoff: Optional[Dict[str, Any]] = None
    payload: Optional[Dict[str, Any]] = None


class DeploymentOpsOutput(BaseModel):
    agent_id: str = "Agent #26"
    agent_name: str = "DeploymentOpsAgent"
    fabric_id: str = "agent.26"
    status: str = "success"  # success, error, access_denied
    project_id: str
    system_id: str
    system_type: SystemType = SystemType.HYBRID
    operation: str
    readiness_status: ReadinessStatus = ReadinessStatus.NOT_ASSESSED
    readiness_criteria: List[DeploymentReadinessCriteria] = Field(default_factory=list)
    deployment_plan: Optional[DeploymentPlan] = None
    installation_requirements: List[InstallationRequirement] = Field(default_factory=list)
    commissioning_plan: Optional[CommissioningPlan] = None
    operational_baseline: Optional[OperationalBaseline] = None
    dependencies: List[OperationalDependency] = Field(default_factory=list)
    health_metrics: List[HealthMetric] = Field(default_factory=list)
    alert_rules: List[AlertRule] = Field(default_factory=list)
    incidents: List[IncidentRecord] = Field(default_factory=list)
    troubleshooting_tree: Optional[TroubleshootingTree] = None
    recovery_plans: List[RecoveryAction] = Field(default_factory=list)
    rollback_plan: Optional[RollbackPlan] = None
    backup_restore_plan: Optional[BackupRestorePlan] = None
    maintenance_tasks: List[MaintenanceTask] = Field(default_factory=list)
    serviceability_evaluations: List[ServiceabilityEvaluation] = Field(default_factory=list)
    spare_parts: List[SparePartRequirement] = Field(default_factory=list)
    decommissioning_plan: Optional[DecommissioningPlan] = None
    report_markdown: Optional[str] = None
    execution_duration_seconds: float = 0.0
    error_message: Optional[str] = None
