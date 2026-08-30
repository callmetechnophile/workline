"""
Pydantic data contracts and schemas for VerificationQAAgent (Agent #12).
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


QAVerdictLiteral = Literal[
    "VERIFIED",
    "VERIFIED_WITH_WARNINGS",
    "FAILED",
    "INCOMPLETE",
    "BLOCKED",
]

StatusLiteral = Literal[
    "PASS",
    "FAIL",
    "UNKNOWN",
    "NOT_APPLICABLE",
    "PARTIAL",
    "SKIPPED",
    "NOT_RUN",
    "ERROR",
]

ChangeTypeLiteral = Literal[
    "created",
    "modified",
    "deleted",
    "unchanged",
    "unexpected",
]

FailureTypeLiteral = Literal[
    "IMPLEMENTATION_FAILURE",
    "TEST_FAILURE",
    "BUILD_FAILURE",
    "ARCHITECTURE_CONFORMANCE_FAILURE",
    "BOM_CONFORMANCE_FAILURE",
    "REQUIREMENT_FAILURE",
    "SECURITY_FAILURE",
    "AUTHORIZATION_FAILURE",
    "SCOPE_FAILURE",
    "DEPENDENCY_FAILURE",
    "INTEGRATION_FAILURE",
    "PERFORMANCE_FAILURE",
    "UNKNOWN_VERIFICATION",
]


class ChangeObject(BaseModel):
    """File inspection and diff verification object (Section 9)."""

    file: str
    expected: bool = True
    actual: bool = True
    change_type: ChangeTypeLiteral = "created"
    authorized: bool = True
    task_id: Optional[str] = None
    status: Literal["PASS", "FAIL"] = "PASS"


class TaskVerificationObject(BaseModel):
    """Individual work package task verification record (Section 11)."""

    task_id: str
    execution_status: str = "completed"
    implementation_status: Literal["PASS", "FAIL", "PARTIAL"] = "PASS"
    acceptance_status: Literal["PASS", "FAIL", "PARTIAL", "UNKNOWN"] = "PASS"
    test_status: Literal["PASS", "FAIL", "PARTIAL", "NOT_RUN"] = "PASS"
    scope_status: Literal["PASS", "FAIL"] = "PASS"
    issues: List[str] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


class RequirementVerificationItem(BaseModel):
    """End-to-end requirement traceability verification item (Section 15)."""

    requirement_id: str
    description: str = ""
    implementation_tasks: List[str] = Field(default_factory=list)
    test_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    status: Literal["PASS", "FAIL", "UNKNOWN"] = "PASS"
    coverage: Literal["complete", "partial", "none"] = "complete"


class EvidenceObject(BaseModel):
    """Cryptographically referenced verification evidence (Section 35)."""

    evidence_id: str
    type: Literal["test", "build", "static_analysis", "runtime", "file", "hardware", "simulation"]
    source: str
    command: Optional[str] = None
    result: str
    timestamp: str
    supports: List[str] = Field(default_factory=list)


class TestResultObject(BaseModel):
    """Execution telemetry for unit/integration/regression tests (Section 36)."""

    __test__ = False

    test_id: str
    command: str
    status: Literal["PASS", "FAIL", "SKIPPED", "ERROR"]
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    duration: Optional[float] = None
    output_reference: Optional[str] = None
    evidence_id: Optional[str] = None


class SecurityFinding(BaseModel):
    """Security scanner audit finding with secret masking (Section 27 & 56)."""

    finding_id: str
    category: Literal["secret", "command_injection", "path_traversal", "prompt_injection", "permissions"]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
    file: str
    line: Optional[int] = None
    masked_snippet: str
    description: str


class ConformanceResult(BaseModel):
    """Architecture or BOM conformance evaluation result (Sections 21, 24, 25)."""

    domain: Literal["architecture", "bom", "procurement"]
    status: Literal["PASS", "FAIL", "WARNING"] = "PASS"
    details: str = ""
    violations: List[str] = Field(default_factory=list)


class CorrectionReportItem(BaseModel):
    """Actionable prescriptive remediation report without code modification (Section 50)."""

    correction_id: str
    failure_id: str
    problem: str
    evidence: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    affected_files: List[str] = Field(default_factory=list)
    recommended_correction: str
    revalidation_required: bool = True


class VerificationTraceabilityItem(BaseModel):
    """Requirement to test to evidence lineage record (Section 52)."""

    traceability_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    architecture_ids: List[str] = Field(default_factory=list)
    task_ids: List[str] = Field(default_factory=list)
    file_paths: List[str] = Field(default_factory=list)
    test_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    verification_status: str = "PASS"


class FinalQAVerdict(BaseModel):
    """Comprehensive final QA quality gate verdict (Section 47)."""

    verdict: QAVerdictLiteral
    requirements_passed: int = 0
    requirements_failed: int = 0
    requirements_unknown: int = 0
    tasks_verified: int = 0
    tasks_failed: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    security_failures: int = 0
    scope_failures: int = 0
    architecture_failures: int = 0
    bom_failures: int = 0
    warnings: int = 0
    unknowns: int = 0
    blocking_issues: List[str] = Field(default_factory=list)
    recommendation: str = ""


class VerificationExecutionContext(BaseModel):
    """Execution context for QA review."""

    user_id: str = "user_001"
    project_id: str = "proj_001"
    agent_id: str = "VerificationQAAgent"
    parent_agent_id: Optional[str] = "ResearchOrchestrator"
    execution_id: Optional[str] = None


class VerificationQAAgentInput(BaseModel):
    """Input contract for Agent #12 (Section 5)."""

    project: Dict[str, Any]
    requirements: List[Dict[str, Any]] = Field(default_factory=list)
    architecture: Dict[str, Any] = Field(default_factory=dict)
    bom: Dict[str, Any] = Field(default_factory=dict)
    procurement: Dict[str, Any] = Field(default_factory=dict)
    validation: Dict[str, Any] = Field(default_factory=dict)
    implementation_plan: Dict[str, Any] = Field(default_factory=dict)
    execution_result: Dict[str, Any] = Field(default_factory=dict)
    changed_files: List[str] = Field(default_factory=list)
    test_results: List[Dict[str, Any]] = Field(default_factory=list)
    execution_context: Optional[VerificationExecutionContext] = None
    project_root_dir: Optional[str] = None
    output_dir: Optional[str] = None
    dry_run: bool = False
    tests_only: bool = False
    requirements_only: bool = False
    security_only: bool = False


class VerificationQAAgentOutput(BaseModel):
    """Output contract for Agent #12 (Section 63)."""

    status: str
    verification_id: str
    project_id: str
    verdict: QAVerdictLiteral
    final_verdict: FinalQAVerdict
    changes: List[ChangeObject] = Field(default_factory=list)
    tasks: List[TaskVerificationObject] = Field(default_factory=list)
    requirements: List[RequirementVerificationItem] = Field(default_factory=list)
    test_results: List[TestResultObject] = Field(default_factory=list)
    evidence: List[EvidenceObject] = Field(default_factory=list)
    security_findings: List[SecurityFinding] = Field(default_factory=list)
    architecture_conformance: ConformanceResult = Field(
        default_factory=lambda: ConformanceResult(
            domain="architecture", status="PASS", details="Architecture verified"
        )
    )
    bom_conformance: ConformanceResult = Field(
        default_factory=lambda: ConformanceResult(
            domain="bom", status="PASS", details="BOM verified"
        )
    )
    authorization_verification: Dict[str, Any] = Field(default_factory=dict)
    corrections: List[CorrectionReportItem] = Field(default_factory=list)
    traceability: List[VerificationTraceabilityItem] = Field(default_factory=list)
    structured_report_markdown: str = ""
