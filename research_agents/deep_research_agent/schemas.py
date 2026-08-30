"""
Data contracts and Pydantic schemas for DeepResearchAgent (Agent #4).
Defines project input, evidence items, synthesized claims (with strict fact/inference separation),
component trade studies, cross-source comparisons, contradictions, and report output.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


EvidenceSourceTypeLiteral = Literal[
    "research_paper",
    "manufacturer_documentation",
    "datasheet",
    "application_note",
    "github_repository",
    "engineering_project",
    "technical_article",
    "tutorial",
    "vendor",
    "standard",
    "other",
]

ClaimTypeLiteral = Literal[
    "explicit_source_claim",
    "derived_claim",
    "model_inference",
    "engineering_recommendation",
    "unknown",
]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "DeepResearchAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class ProjectMeta(BaseModel):
    """Engineering project scope and contextual constraints."""

    project_id: Optional[str] = None
    title: str = Field(..., description="Project title or concept name.")
    description: Optional[str] = Field(default=None, description="Detailed problem statement.")
    engineering_domain: Optional[str] = Field(default=None, description="Engineering discipline.")
    objectives: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)


class EvidenceItem(BaseModel):
    """Normalized evidence item derived from upstream agents (Papers, Web, Processed Docs)."""

    evidence_id: str
    source_id: str
    document_id: Optional[str] = None
    source_type: EvidenceSourceTypeLiteral = "other"
    source_url: Optional[str] = None
    title: Optional[str] = None
    text: str
    page: Optional[int] = None
    section: Optional[str] = None
    publication_date: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SynthesizedClaim(BaseModel):
    """A verified assertion categorized strictly into facts, inferences, or recommendations."""

    claim: str
    claim_type: ClaimTypeLiteral
    source_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    rationale: Optional[str] = None


class ComponentTradeStudy(BaseModel):
    """Engineering trade study comparing candidate hardware or software components."""

    component_type: str  # e.g., "Edge AI Compute Module", "Thermal Sensor"
    candidates_evaluated: List[str]
    tradeoff_matrix: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    recommended_option: str
    recommendation_reason: str


class CrossSourceComparison(BaseModel):
    """Cross-source comparison identifying consensus or diversity of findings."""

    topic: str
    sources_agree: bool = True
    summary: str
    evidence_ids: List[str] = Field(default_factory=list)


class ContradictionReport(BaseModel):
    """Discrepancy or contradiction detected across research papers and vendor specs."""

    topic: str
    source_a_claim: str
    source_a_evidence_id: str
    source_b_claim: str
    source_b_evidence_id: str
    resolution: str


class EngineeringImplication(BaseModel):
    """Technical consequence on hardware design, firmware, power, or latency."""

    category: str  # power, compute, latency, thermal, cost, mechanical
    finding: str
    impact_on_project: str


class EngineeringRecommendation(BaseModel):
    """Project-specific actionable engineering guidance."""

    recommendation: str
    category: str
    priority: Literal["high", "medium", "low"] = "medium"
    justification: str
    backed_by_claims: List[str] = Field(default_factory=list)


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class DeepResearchAgentInput(BaseModel):
    """Structured input contract for DeepResearchAgent."""

    project: ProjectMeta
    research_papers: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Candidate academic research papers from Agent #1 (ResearchPaperAgent).",
    )
    web_sources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Normalized web evidence sources from Agent #2 (WebResearchAgent).",
    )
    documents: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Processed document outputs from Agent #3 (DocumentProcessingAgent).",
    )
    chunks: List[Dict[str, Any]] = Field(default_factory=list)
    facts: List[Dict[str, Any]] = Field(default_factory=list)
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    references: List[Dict[str, Any]] = Field(default_factory=list)
    execution_context: Optional[RequestContext] = None


class DeepResearchAgentOutput(BaseModel):
    """Structured synthesis report output contract for DeepResearchAgent."""

    status: Literal["success", "error"] = "success"
    project: ProjectMeta
    executive_summary: str = ""
    architecture_analysis: str = ""
    component_trade_studies: List[ComponentTradeStudy] = Field(default_factory=list)
    extracted_claims: List[SynthesizedClaim] = Field(default_factory=list)
    cross_source_comparisons: List[CrossSourceComparison] = Field(default_factory=list)
    contradictions: List[ContradictionReport] = Field(default_factory=list)
    engineering_implications: List[EngineeringImplication] = Field(default_factory=list)
    recommendations: List[EngineeringRecommendation] = Field(default_factory=list)
    research_gaps: List[str] = Field(default_factory=list)
    evidence_used: List[EvidenceItem] = Field(default_factory=list)
    structured_markdown_report: str = ""
    errors: List[StructuredError] = Field(default_factory=list)
