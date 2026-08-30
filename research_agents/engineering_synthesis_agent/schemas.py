"""
Data contracts and Pydantic schemas for EngineeringSynthesisAgent (Agent #5).
Defines project inputs, requirement mappings, technical findings, engineering trade-offs,
design decisions, recommendations, assumptions, unknowns, risks, validation plans, and complete traceability.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


RequirementCoverageLiteral = Literal["strong", "partial", "weak", "unsupported"]

RecommendationCategoryLiteral = Literal[
    "hardware",
    "software",
    "architecture",
    "algorithm",
    "communication",
    "power",
    "thermal",
    "deployment",
]

RiskCategoryLiteral = Literal[
    "technical",
    "hardware",
    "software",
    "integration",
    "power",
    "thermal",
    "communication",
    "manufacturing",
    "availability",
    "cost",
    "regulatory",
    "security",
    "deployment",
]

ValidationCategoryLiteral = Literal[
    "bench_test",
    "datasheet_verification",
    "prototype_measurement",
    "benchmark",
    "unit_test",
    "integration_test",
    "simulation",
]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "EngineeringSynthesisAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class ProjectMeta(BaseModel):
    """Engineering project scope, requirements, and constraints."""

    project_id: Optional[str] = None
    title: str = Field(..., description="Project title or concept name.")
    description: Optional[str] = Field(default=None, description="Detailed problem statement.")
    engineering_domain: Optional[str] = Field(default=None, description="Engineering discipline.")
    objectives: List[str] = Field(default_factory=list)
    requirements: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    budget: Optional[str] = None
    timeline: Optional[str] = None


class RequirementAnalysis(BaseModel):
    """Project requirement mapped to supporting evidence and decision coverage."""

    requirement_id: str
    requirement: str
    coverage: RequirementCoverageLiteral = "partial"
    evidence_count: int = 0
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    technical_findings: List[str] = Field(default_factory=list)
    decision_available: bool = True
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TechnicalFinding(BaseModel):
    """Specific technical finding derived from research evidence."""

    finding_id: str
    category: str  # architecture, compute, latency, memory, power, thermal, communication, manufacturing
    finding: str
    evidence_ids: List[str] = Field(default_factory=list)
    impact_on_project: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class TradeoffOption(BaseModel):
    """Candidate option evaluated within an engineering trade-off."""

    option: str
    advantages: List[str] = Field(default_factory=list)
    disadvantages: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)


class EngineeringTradeoff(BaseModel):
    """Trade-off analysis comparing hardware/software options."""

    tradeoff_id: str
    decision_area: str
    options: List[TradeoffOption] = Field(default_factory=list)
    recommended_option: str
    reasoning: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class EngineeringDecision(BaseModel):
    """Concrete engineering decision made for the project (Section 23)."""

    decision_id: str
    decision_area: str
    selected_option: str
    alternatives: List[str] = Field(default_factory=list)
    decision_reason: str
    tradeoffs: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    requirement_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_required: bool = True


class RecommendationItem(BaseModel):
    """Specific engineering recommendation (Section 22)."""

    recommendation_id: str
    category: RecommendationCategoryLiteral = "architecture"
    recommendation: str
    reason: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    supporting_requirement_ids: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    validation_required: bool = True


class AssumptionItem(BaseModel):
    """Explicitly documented engineering assumption (Section 11)."""

    assumption_id: str
    assumption: str
    impact: str
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    validation_required: bool = True


class UnknownItem(BaseModel):
    """Missing or currently indeterminable information (Section 12)."""

    unknown_id: str
    unknown: str
    why_it_matters: str
    required_information: str
    blocking: bool = False


class EngineeringRisk(BaseModel):
    """Qualitative engineering risk analysis item (Section 13)."""

    risk_id: str
    category: RiskCategoryLiteral = "technical"
    description: str
    likelihood: Literal["low", "medium", "high"] = "medium"
    impact: Literal["low", "medium", "high"] = "medium"
    severity: Literal["low", "medium", "high"] = "medium"
    mitigation: str
    evidence_ids: List[str] = Field(default_factory=list)
    validation_required: bool = True


class ValidationRequirement(BaseModel):
    """Verification & validation requirement (Section 14)."""

    validation_id: str
    category: ValidationCategoryLiteral = "bench_test"
    description: str
    acceptance_criteria: str
    decision_ids: List[str] = Field(default_factory=list)


class ExperimentPlan(BaseModel):
    """Empirical experiment proposed when evidence is insufficient (Section 15)."""

    experiment_id: str
    question: str
    setup: List[str] = Field(default_factory=list)
    variables: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)


class DecisionTraceability(BaseModel):
    """Unbroken lineage from requirement to validation (Section 17)."""

    decision_id: str
    requirement_ids: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    finding_ids: List[str] = Field(default_factory=list)
    tradeoff_id: Optional[str] = None
    decision: str
    reasoning: str
    validation_ids: List[str] = Field(default_factory=list)


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class EngineeringSynthesisAgentInput(BaseModel):
    """Structured input contract for EngineeringSynthesisAgent (Section 1)."""

    project: ProjectMeta
    deep_research: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured synthesis report from Agent #4 (DeepResearchAgent).",
    )
    research_papers: List[Dict[str, Any]] = Field(default_factory=list)
    web_sources: List[Dict[str, Any]] = Field(default_factory=list)
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    relationships: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    code_blocks: List[Dict[str, Any]] = Field(default_factory=list)
    output_dir: Optional[str] = Field(
        default=None,
        description="Optional directory to export the 5 required JSON & Markdown artifacts.",
    )
    execution_context: Optional[RequestContext] = None


class EngineeringSynthesisAgentOutput(BaseModel):
    """Structured output contract for EngineeringSynthesisAgent (Section 21)."""

    status: Literal["success", "error"] = "success"
    project: ProjectMeta
    requirement_analysis: List[RequirementAnalysis] = Field(default_factory=list)
    technical_findings: List[TechnicalFinding] = Field(default_factory=list)
    tradeoffs: List[EngineeringTradeoff] = Field(default_factory=list)
    decisions: List[EngineeringDecision] = Field(default_factory=list)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
    assumptions: List[AssumptionItem] = Field(default_factory=list)
    unknowns: List[UnknownItem] = Field(default_factory=list)
    risks: List[EngineeringRisk] = Field(default_factory=list)
    validation_requirements: List[ValidationRequirement] = Field(default_factory=list)
    experiments: List[ExperimentPlan] = Field(default_factory=list)
    traceability: List[DecisionTraceability] = Field(default_factory=list)
    overall_confidence: float = Field(default=0.85, ge=0.0, le=1.0)
    structured_report_markdown: str = ""
    warnings: List[str] = Field(default_factory=list)
    errors: List[StructuredError] = Field(default_factory=list)
