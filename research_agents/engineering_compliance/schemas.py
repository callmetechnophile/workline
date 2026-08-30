"""
Pydantic data contracts and schemas for EngineeringComplianceAgent (Agent #17).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


ComplianceDomainLiteral = Literal[
    "ELECTRICAL",
    "ELECTRONICS",
    "POWER",
    "THERMAL",
    "MECHANICAL",
    "SOFTWARE",
    "FIRMWARE",
    "COMMUNICATION",
    "INTERFACE",
    "BOM",
    "PROCUREMENT",
    "MANUFACTURING",
    "ENVIRONMENTAL",
    "SAFETY",
    "SECURITY",
    "PROJECT_REQUIREMENTS",
    "CUSTOM_DESIGN_RULES",
    "APPLICABLE_STANDARDS",
]

ComplianceStatusLiteral = Literal[
    "PASS",
    "FAIL",
    "WARNING",
    "REVIEW",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "INVALIDATED",
]

ComplianceSeverityLiteral = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

ComplianceGateLiteral = Literal[
    "ALLOW",
    "BLOCK",
    "REVIEW_REQUIRED",
    "INSUFFICIENT_EVIDENCE",
    "ALLOW_WITH_APPROVED_EXCEPTION",
]

RuleTypeLiteral = Literal[
    "LIMIT_RULE",
    "RANGE_RULE",
    "EQUALITY_RULE",
    "ENUM_RULE",
    "DEPENDENCY_RULE",
    "COMPATIBILITY_RULE",
    "REQUIREMENT_RULE",
    "INTERFACE_RULE",
    "POWER_RULE",
    "THERMAL_RULE",
    "MECHANICAL_RULE",
    "BOM_RULE",
    "PROCESS_RULE",
    "CUSTOM_RULE",
]

RuleSourceLiteral = Literal[
    "PROJECT_REQUIREMENT",
    "ENGINEERING_SPECIFICATION",
    "USER_DEFINED_RULE",
    "VALIDATED_COMPONENT_DATASHEET",
    "APPROVED_STANDARD",
    "VALIDATED_RESEARCH",
    "DESIGN_CONSTRAINT",
    "SYSTEM_POLICY",
]


class ComplianceRule(BaseModel):
    """Authoritative engineering design or compliance rule (Section 7)."""

    rule_id: str
    project_id: str
    name: str
    description: str
    domain: ComplianceDomainLiteral
    severity: ComplianceSeverityLiteral = "HIGH"
    rule_type: RuleTypeLiteral = "LIMIT_RULE"
    expression: str
    source: RuleSourceLiteral = "PROJECT_REQUIREMENT"
    source_reference: Optional[str] = None
    version: str = "v1.0.0"
    enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class StandardReference(BaseModel):
    """Authoritative standard reference metadata (Section 31)."""

    standard_id: str
    name: str
    version: str
    source: str
    reference: str
    applicability: str
    authority: str = "APPROVED"


class ComplianceResult(BaseModel):
    """Traceable evaluation result for an artifact against a compliance rule (Section 6)."""

    compliance_id: str
    project_id: str
    artifact_id: str
    artifact_type: str
    domain: ComplianceDomainLiteral
    status: ComplianceStatusLiteral
    severity: ComplianceSeverityLiteral
    rule_id: str
    requirement_id: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    description: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ComplianceException(BaseModel):
    """Approved engineering exception for a known deviation (Section 43)."""

    exception_id: str
    compliance_id: str
    reason: str
    risk: str
    approved_by: str
    approval_type: str = "ENGINEERING_EXCEPTION"
    expires_at: Optional[str] = None
    status: Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED"] = "PENDING"


class ComplianceWaiver(BaseModel):
    """Scoped, expiring compliance waiver (Section 45)."""

    waiver_id: str
    project_id: str
    rule_id: str
    artifact_id: str
    reason: str
    risk: str
    approved_by: str
    expires_at: str
    status: Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED"] = "APPROVED"


class ComplianceMatrixItem(BaseModel):
    """Row item in the compliance traceability matrix (Section 60)."""

    requirement_id: str
    rule_id: str
    artifact_id: str
    evidence_id: str
    result: ComplianceStatusLiteral
    severity: ComplianceSeverityLiteral


class ProjectComplianceSummary(BaseModel):
    """Executive compliance dashboard and gate summary (Section 54)."""

    project_id: str
    status: ComplianceStatusLiteral
    gate: ComplianceGateLiteral
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    review_required: int = 0
    unknown: int = 0
    critical_failures: int = 0
    high_failures: int = 0
    blocking: bool = False


class ComplianceInput(BaseModel):
    """Input payload for EngineeringComplianceAgent."""

    project_id: str
    user_id: str = "user_001"
    team_id: Optional[str] = None
    target_artifact: Optional[str] = None
    domain_filter: Optional[ComplianceDomainLiteral] = None
    output_dir: Optional[str] = None


class ComplianceOutput(BaseModel):
    """Output payload returned by EngineeringComplianceAgent."""

    summary: ProjectComplianceSummary
    results: List[ComplianceResult] = Field(default_factory=list)
    matrix: List[ComplianceMatrixItem] = Field(default_factory=list)
    waivers: List[ComplianceWaiver] = Field(default_factory=list)
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
