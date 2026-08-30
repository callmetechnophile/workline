"""
Data contracts and Pydantic schemas for EngineeringValidationAgent (Agent #9).
Defines validation items, severities, statuses, verdicts, required corrections,
traceability, and 10-file export contracts.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

ValidationStatusLiteral = Literal["PASS", "FAIL", "WARNING", "UNKNOWN", "NOT_APPLICABLE"]
ValidationSeverityLiteral = Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
VerdictLiteral = Literal["READY", "READY_WITH_WARNINGS", "BLOCKED", "INCOMPLETE"]
RequirementCoverageLiteral = Literal["STRONG", "PARTIAL", "WEAK", "UNSUPPORTED", "UNKNOWN"]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration (Section 44)."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "EngineeringValidationAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class ValidationItem(BaseModel):
    """Atomic design rule check result or verification finding (Section 8 & 36)."""

    validation_id: str
    rule_id: Optional[str] = None
    category: str  # electrical, power, interface, resource, software, ai_ml, thermal, mechanical, bom, procurement, architecture, requirement
    status: ValidationStatusLiteral = "PASS"
    severity: ValidationSeverityLiteral = "INFO"
    title: str
    description: str
    affected_components: List[str] = Field(default_factory=list)
    affected_subsystems: List[str] = Field(default_factory=list)
    requirement_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    source_data: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_action: Optional[str] = None
    blocking: bool = False


class RequirementValidationItem(BaseModel):
    """Requirement traceability and coverage verification item (Sections 9 & 10)."""

    requirement_id: str
    description: str
    status: ValidationStatusLiteral = "PASS"
    coverage: RequirementCoverageLiteral = "STRONG"
    architecture_supported: bool = True
    bom_supported: bool = True
    procurement_supported: bool = True
    validation_available: bool = True
    notes: Optional[str] = None


class RequiredCorrection(BaseModel):
    """Prescriptive engineering correction for a blocking failure (Section 49)."""

    correction_id: str
    validation_id: str
    problem: str
    why_it_matters: str
    recommended_correction: str
    affected_components: List[str] = Field(default_factory=list)
    affected_subsystems: List[str] = Field(default_factory=list)
    blocking: bool = True


class FinalVerdict(BaseModel):
    """Aggregate engineering quality gate decision (Section 38)."""

    verdict: VerdictLiteral = "READY"
    critical_failures: int = 0
    high_failures: int = 0
    medium_failures: int = 0
    warnings: int = 0
    unknowns: int = 0
    requirements_passed: int = 0
    requirements_failed: int = 0
    requirements_unknown: int = 0
    recommendation: str = "Design satisfies all engineering rules and is ready for execution."


class ValidationTraceabilityItem(BaseModel):
    """Full unbroken lineage from Requirement -> Architecture -> Component -> BOM -> Procurement -> Rule -> Verdict (Section 46)."""

    traceability_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    architecture_ids: List[str] = Field(default_factory=list)
    component_ids: List[str] = Field(default_factory=list)
    bom_item_ids: List[str] = Field(default_factory=list)
    procurement_ids: List[str] = Field(default_factory=list)
    validation_ids: List[str] = Field(default_factory=list)
    status: str = "PASS"
    verdict_impact: str = "READY"


class StructuredError(BaseModel):
    """Machine-readable error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class EngineeringValidationAgentInput(BaseModel):
    """Structured input contract for EngineeringValidationAgent (Section 5)."""

    project: Dict[str, Any] = Field(default_factory=dict)
    engineering_synthesis: Dict[str, Any] = Field(default_factory=dict)
    architecture: Dict[str, Any] = Field(default_factory=dict)
    subsystems: List[Dict[str, Any]] = Field(default_factory=list)
    component_roles: List[Dict[str, Any]] = Field(default_factory=list)
    interfaces: List[Dict[str, Any]] = Field(default_factory=list)
    power_domains: List[Dict[str, Any]] = Field(default_factory=list)
    data_flows: List[Dict[str, Any]] = Field(default_factory=list)
    control_flows: List[Dict[str, Any]] = Field(default_factory=list)
    dependencies: List[Dict[str, Any]] = Field(default_factory=list)
    bom: Dict[str, Any] = Field(default_factory=dict)
    optimized_procurement: Dict[str, Any] = Field(default_factory=dict)
    engineering_decisions: List[Dict[str, Any]] = Field(default_factory=list)
    risks: List[Dict[str, Any]] = Field(default_factory=list)
    validation_requirements: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional directory to export the 10 validation artifacts.",
    )
    execution_context: Optional[RequestContext] = None


class EngineeringValidationAgentOutput(BaseModel):
    """Structured output contract for EngineeringValidationAgent (Section 48)."""

    status: Literal["success", "error"] = "success"
    project_id: str = ""
    validation_id: str = "VAL-001"
    verdict: VerdictLiteral = "READY"
    requirement_results: List[RequirementValidationItem] = Field(default_factory=list)
    architecture_results: List[ValidationItem] = Field(default_factory=list)
    electrical_results: List[ValidationItem] = Field(default_factory=list)
    power_results: List[ValidationItem] = Field(default_factory=list)
    interface_results: List[ValidationItem] = Field(default_factory=list)
    resource_results: List[ValidationItem] = Field(default_factory=list)
    software_results: List[ValidationItem] = Field(default_factory=list)
    ai_ml_results: List[ValidationItem] = Field(default_factory=list)
    thermal_results: List[ValidationItem] = Field(default_factory=list)
    mechanical_results: List[ValidationItem] = Field(default_factory=list)
    bom_results: List[ValidationItem] = Field(default_factory=list)
    procurement_results: List[ValidationItem] = Field(default_factory=list)
    rule_results: List[ValidationItem] = Field(default_factory=list)
    critical_failures: List[ValidationItem] = Field(default_factory=list)
    warnings: List[ValidationItem] = Field(default_factory=list)
    unknowns: List[ValidationItem] = Field(default_factory=list)
    required_corrections: List[RequiredCorrection] = Field(default_factory=list)
    traceability: List[ValidationTraceabilityItem] = Field(default_factory=list)
    final_verdict: FinalVerdict = Field(default_factory=FinalVerdict)
    confidence: float = Field(default=0.98, ge=0.0, le=1.0)
    structured_report_markdown: str = ""
    errors: List[StructuredError] = Field(default_factory=list)
