"""Data models and enums for the Engineering Requirement & Validation Engine."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class RequirementCategory(str, Enum):
    ELECTRICAL = "ELECTRICAL"
    POWER = "POWER"
    MECHANICAL = "MECHANICAL"
    THERMAL = "THERMAL"
    COMMUNICATION = "COMMUNICATION"
    COMPUTE = "COMPUTE"
    MEMORY = "MEMORY"
    SENSOR = "SENSOR"
    ACTUATOR = "ACTUATOR"
    SAFETY = "SAFETY"
    ENVIRONMENTAL = "ENVIRONMENTAL"
    PCB = "PCB"
    SOFTWARE = "SOFTWARE"
    PERFORMANCE = "PERFORMANCE"
    PROCUREMENT = "PROCUREMENT"
    OTHER = "OTHER"


class ValidationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
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
    BETWEEN = "BETWEEN"
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"


class EngineeringConstraint(BaseModel):
    constraint_id: str
    property: str
    operator: ConstraintOperator
    required_value: str
    required_unit: Optional[str] = None
    normalized_value: float = 0.0
    dimension: str = "VOLTAGE"
    tolerance: Optional[Dict[str, Any]] = None
    source: Optional[str] = None


class EngineeringRequirement(BaseModel):
    requirement_id: str
    project_id: str
    team_id: str = "default_team"
    category: RequirementCategory = RequirementCategory.ELECTRICAL
    description: str
    constraints: List[EngineeringConstraint] = Field(default_factory=list)
    priority: str = "HIGH"
    status: str = "ACTIVE"
    source: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)


class ConstraintResult(BaseModel):
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
    validation_id: str
    candidate_id: str
    requirement_id: str
    overall_status: ValidationStatus
    constraint_results: List[ConstraintResult] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    rule_version: str = "electrical_rules_v1"
    knowledge_version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)
