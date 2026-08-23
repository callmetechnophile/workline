"""
Data models and enums for the Engineering Requirement & Validation Engine.
Provides distinct structures for Requirements (Objectives), Constraints (Design Limits), and Validation.
"""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RequirementCategory(str, Enum):
    """Broad functional and domain classifications for engineering requirements."""
    SYSTEM = "SYSTEM"
    FUNCTIONAL = "FUNCTIONAL"
    PERFORMANCE = "PERFORMANCE"
    ELECTRICAL = "ELECTRICAL"
    POWER = "POWER"
    MECHANICAL = "MECHANICAL"
    THERMAL = "THERMAL"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    INTERFACE = "INTERFACE"
    COMPLIANCE = "COMPLIANCE"
    COST = "COST"
    SCHEDULE = "SCHEDULE"
    RELIABILITY = "RELIABILITY"
    SAFETY = "SAFETY"
    COMMUNICATION = "COMMUNICATION"
    COMPUTE = "COMPUTE"
    MEMORY = "MEMORY"
    SENSOR = "SENSOR"
    ACTUATOR = "ACTUATOR"
    PCB = "PCB"
    SOFTWARE = "SOFTWARE"
    PROCUREMENT = "PROCUREMENT"
    OTHER = "OTHER"


class RequirementPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequirementStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    WAIVED = "WAIVED"


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class ConstraintOperator(str, Enum):
    EQ = "="
    NEQ = "!="
    GT = ">"
    GTE = ">="
    LT = "<"
    LTE = "<="
    IN = "IN"
    NOT_IN = "NOT_IN"
    RANGE = "RANGE"
    BETWEEN = "BETWEEN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"


class ConstraintSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class ConstraintStatus(str, Enum):
    ACTIVE = "ACTIVE"
    SATISFIED = "SATISFIED"
    VIOLATED = "VIOLATED"
    PENDING = "PENDING"
    WAIVED = "WAIVED"


class EngineeringConstraint(BaseModel):
    """Design limitation or boundary that must not be violated."""
    constraint_id: str
    project_id: Optional[str] = None
    requirement_id: Optional[str] = None  # Link to justifying requirement
    property: str = Field(description="Parameter or property name (e.g. output_voltage, max_temp)")
    operator: ConstraintOperator = ConstraintOperator.LTE
    required_value: str = Field(description="Target threshold or limit value")
    required_unit: Optional[str] = None
    normalized_value: float = 0.0
    dimension: str = "VOLTAGE"
    category: Optional[str] = "ELECTRICAL"
    severity: ConstraintSeverity = ConstraintSeverity.CRITICAL
    status: ConstraintStatus = ConstraintStatus.ACTIVE
    verification_method: Optional[str] = "Simulation"
    tolerance: Optional[Dict[str, Any]] = None
    source: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class EngineeringRequirement(BaseModel):
    """High-level objective or specification answering 'What must the system achieve?'"""
    requirement_id: str
    project_id: str
    title: Optional[str] = None
    description: str
    category: RequirementCategory = RequirementCategory.ELECTRICAL
    parameter: Optional[str] = None
    target_value: Optional[str] = None
    unit: Optional[str] = None
    priority: RequirementPriority = RequirementPriority.HIGH
    status: RequirementStatus = RequirementStatus.ACTIVE
    verification_method: Optional[str] = "Simulation"  # Simulation, Test, Inspection, Analysis, Datasheet
    source: Optional[str] = None  # Document, Standard, Stakeholder, Datasheet
    constraints: List[EngineeringConstraint] = Field(default_factory=list)
    team_id: str = "default_team"
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class ConstraintResult(BaseModel):
    """Verification outcome of a single constraint."""
    constraint_id: str
    property: str
    required_value: str
    actual_value: str
    operator: str
    status: ValidationStatus
    unit: Optional[str] = None
    source_document: Optional[str] = None
    page: Optional[int] = None
    section: Optional[str] = None
    reason: str


class ValidationResult(BaseModel):
    """Aggregated validation output across requirements and constraints."""
    validation_id: str
    candidate_id: Optional[str] = None
    requirement_id: str
    project_id: Optional[str] = None
    overall_status: ValidationStatus
    constraint_results: List[ConstraintResult] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    rule_version: str = "electrical_rules_v1"
    knowledge_version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)


class RequirementOverviewSummary(BaseModel):
    """Consolidated metrics for project requirements & constraints."""
    project_id: str
    project_name: Optional[str] = None
    total_requirements: int = 0
    total_constraints: int = 0
    validated_count: int = 0
    pending_count: int = 0
    violations_count: int = 0
    overall_status: ValidationStatus = ValidationStatus.PENDING
    last_updated: float = Field(default_factory=time.time)
