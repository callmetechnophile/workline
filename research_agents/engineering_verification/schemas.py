"""
Pydantic data contracts and schemas for EngineeringVerificationAgent (Agent #18).
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


VerificationMethodLiteral = Literal[
    "ANALYSIS",
    "INSPECTION",
    "TEST",
    "MEASUREMENT",
    "SIMULATION",
    "CALCULATION",
    "REVIEW",
    "DEMONSTRATION",
    "STATIC_ANALYSIS",
    "DYNAMIC_TEST",
    "HARDWARE_TEST",
    "SOFTWARE_TEST",
    "INTEGRATION_TEST",
    "SYSTEM_TEST",
    "ACCEPTANCE_TEST",
]

VerificationStatusLiteral = Literal[
    "NOT_PLANNED",
    "PLANNED",
    "TEST_READY",
    "RUNNING",
    "PASS",
    "FAIL",
    "BLOCKED",
    "REVIEW",
    "UNKNOWN",
    "INVALIDATED",
    "VERIFIED",
]

TestTypeLiteral = Literal[
    "UNIT",
    "INTEGRATION",
    "SYSTEM",
    "END_TO_END",
    "REGRESSION",
    "PERFORMANCE",
    "STRESS",
    "LOAD",
    "POWER",
    "THERMAL",
    "ELECTRICAL",
    "COMMUNICATION",
    "INTERFACE",
    "HARDWARE",
    "FIRMWARE",
    "SOFTWARE",
    "SECURITY",
    "SAFETY",
    "FUNCTIONAL",
    "NON_FUNCTIONAL",
    "ACCEPTANCE",
]

TestStatusLiteral = Literal[
    "PLANNED",
    "NOT_EXECUTED",
    "RUNNING",
    "PASS",
    "FAIL",
    "BLOCKED",
    "ERROR",
    "INCONCLUSIVE",
    "INVALIDATED",
]

EvidenceTypeLiteral = Literal[
    "LOG",
    "MEASUREMENT",
    "SCREENSHOT",
    "VIDEO",
    "TRACE",
    "TEST_RESULT",
    "SIMULATION",
    "REPORT",
    "DOCUMENT",
]


class TestObject(BaseModel):
    """Authoritative test case specification (Section 10)."""

    __test__ = False

    test_id: str
    project_id: str
    verification_id: Optional[str] = None
    name: str
    type: TestTypeLiteral = "UNIT"
    objective: str
    preconditions: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    expected_results: Dict[str, Any] = Field(default_factory=dict)
    acceptance_criteria: List[str] = Field(default_factory=list)
    tolerance: Optional[Dict[str, float]] = None
    status: TestStatusLiteral = "PLANNED"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    executed_at: Optional[str] = None


class MeasurementObject(BaseModel):
    """Instrumented engineering measurement evidence (Section 16)."""

    measurement_id: str
    test_id: str
    parameter: str
    value: float
    unit: str
    instrument: str
    accuracy: str = "±0.5%"
    conditions: str = "25°C ambient, 1 atm"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    operator: str = "automated_test_runner"


class SimulationObject(BaseModel):
    """Simulation run evidence and artifacts (Section 20)."""

    simulation_id: str
    test_id: str
    tool: str
    tool_version: str
    model: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    result: Literal["PASS", "FAIL", "REVIEW"] = "PASS"
    artifacts: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EvidenceObject(BaseModel):
    """Immutable hashed verification evidence artifact (Section 36)."""

    evidence_id: str
    type: EvidenceTypeLiteral
    source: str
    artifact: str
    artifact_version: str = "v1.0.0"
    hash: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified: bool = True
    status: Literal["VALID", "INVALIDATED"] = "VALID"


class TestResult(BaseModel):
    """Result of an executed test (Section 43)."""

    __test__ = False

    test_result_id: str
    test_id: str
    status: TestStatusLiteral
    actual_results: Dict[str, Any] = Field(default_factory=dict)
    expected_results: Dict[str, Any] = Field(default_factory=dict)
    deviations: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    environment_id: str = "env_sandbox_001"
    executed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class VerificationPlan(BaseModel):
    """Complete verification plan for a project (Section 7)."""

    verification_plan_id: str
    project_id: str
    requirements: List[str] = Field(default_factory=list)
    verification_items: List[str] = Field(default_factory=list)
    methods: List[VerificationMethodLiteral] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    software: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    status: Literal["DRAFT", "APPROVED", "RUNNING", "COMPLETE"] = "APPROVED"


class VerificationMatrixItem(BaseModel):
    """Row in requirement verification matrix (Section 65)."""

    requirement_id: str
    verification_id: str
    test_id: str
    method: VerificationMethodLiteral
    acceptance_criteria: str
    result: TestStatusLiteral
    evidence_id: str
    version: str = "v1.0.0"
    status: VerificationStatusLiteral


class VerificationCoverage(BaseModel):
    """Verification and test coverage metrics (Section 66)."""

    project_id: str
    total_requirements: int = 0
    verified_requirements: int = 0
    failed_requirements: int = 0
    blocked_requirements: int = 0
    pending_requirements: int = 0
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    blocked_tests: int = 0
    unexecuted_tests: int = 0
    total_evidence: int = 0
    coverage_percentage: float = 0.0


class VerificationInput(BaseModel):
    """Input payload for EngineeringVerificationAgent."""

    project_id: str
    user_id: str = "user_001"
    team_id: Optional[str] = None
    target_test: Optional[str] = None
    target_requirement: Optional[str] = None
    output_dir: Optional[str] = None


class VerificationOutput(BaseModel):
    """Output payload returned by EngineeringVerificationAgent."""

    plan: VerificationPlan
    tests: List[TestObject] = Field(default_factory=list)
    results: List[TestResult] = Field(default_factory=list)
    measurements: List[MeasurementObject] = Field(default_factory=list)
    evidence: List[EvidenceObject] = Field(default_factory=list)
    matrix: List[VerificationMatrixItem] = Field(default_factory=list)
    coverage: VerificationCoverage
    report_markdown: str = ""
    exported_files: List[str] = Field(default_factory=list)
