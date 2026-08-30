"""
Data contracts and Pydantic schemas for WebResearchAgent (Agent #2).
Defines structured input, web sources, engineering facts with provenance, and output schemas.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator


SourceTypeEnum = Literal[
    "official_documentation",
    "manufacturer",
    "datasheet",
    "application_note",
    "github_repository",
    "engineering_project",
    "technical_article",
    "tutorial",
    "technical_blog",
    "standard",
    "vendor",
    "product_page",
    "documentation",
    "forum",
    "other",
]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "WebResearchAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class WebResearchAgentInput(BaseModel):
    """Structured input contract for WebResearchAgent."""

    project_title: str = Field(
        ...,
        description="The title or core concept of the engineering project.",
        min_length=1,
    )
    project_description: str = Field(
        ...,
        description="Detailed description of the engineering system, requirements, and hardware.",
        min_length=1,
    )
    engineering_domain: Optional[str] = Field(
        default=None,
        description="Discipline or domain (e.g. Robotics, Power Electronics, Embedded Systems).",
    )
    research_objectives: List[str] = Field(
        default_factory=list,
        description="Specific technical topics, validation needs, or component inquiries.",
    )
    components: List[str] = Field(
        default_factory=list,
        description="Hardware/software components to investigate (e.g. Jetson Orin Nano, ESP32-S3).",
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Algorithms, frameworks, protocols (e.g. YOLO, ROS 2, CAN bus).",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Operational constraints (e.g. real-time inference, low power, 24V supply).",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Search keywords and domain terminology.",
    )
    target_sources: List[str] = Field(
        default_factory=list,
        description="Preferred source categories (e.g. 'GitHub', 'manufacturer documentation', 'datasheets').",
    )
    max_sources: int = Field(
        default=20,
        description="Maximum number of web sources to return (default 20, max 50).",
        ge=1,
        le=50,
    )
    request_context: Optional[RequestContext] = Field(
        default=None,
        description="Optional ArmorIQ / A2A execution context.",
    )

    @field_validator("project_title", "project_description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class RawWebResult(BaseModel):
    """Raw record returned by Tavily or Anakin prior to normalization."""

    title: str
    url: str
    content: Optional[str] = None
    snippet: Optional[str] = None
    raw_html: Optional[str] = None
    published_date: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    source_tool: str = "tavily"  # "tavily" or "anakin"
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class NormalizedWebSource(BaseModel):
    """Normalized, classified, deduplicated, and ranked web evidence source."""

    source_id: str = Field(..., description="Unique source identifier or canonical hash.")
    title: str = Field(..., description="Source webpage or repository title.")
    url: str = Field(..., description="Canonical web URL.")
    domain: str = Field(..., description="Extracted web domain (e.g. github.com, ti.com).")
    source_type: str = Field(
        default="other",
        description="Classified source category (e.g. official_documentation, github_repository).",
    )
    publisher: Optional[str] = Field(default=None, description="Publisher organization or vendor.")
    author: Optional[str] = Field(default=None, description="Author if explicitly known.")
    published_date: Optional[str] = Field(default=None, description="Publication or release date.")
    description: Optional[str] = Field(default=None, description="Summary or snippet description.")
    extracted_content: Optional[str] = Field(default=None, description="Detailed text extracted from page.")
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score between 0.0 and 1.0.",
    )
    relevance_reasons: List[str] = Field(
        default_factory=list,
        description="Verifiable explanations for the assigned relevance score.",
    )
    authority_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Heuristic domain/source authority score between 0.0 and 1.0.",
    )
    authority_reasons: List[str] = Field(
        default_factory=list,
        description="Reasons justifying the assigned authority score.",
    )
    source_tool: str = Field(default="tavily", description="Tool used to discover/extract ('tavily' | 'anakin').")
    accessed_at: str = Field(..., description="ISO timestamp of when the source was retrieved.")
    content_available: bool = Field(default=True, description="True if substantive content was extracted.")


class ExtractedEngineeringFact(BaseModel):
    """Structured technical fact or parameter with complete provenance."""

    fact: str = Field(..., description="Specific extracted engineering fact, specification, or metric.")
    source_id: str = Field(..., description="Identifier of the origin source.")
    source_url: str = Field(..., description="Origin web URL.")
    extraction_method: str = Field(default="tavily", description="Extraction tool or method.")
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Confidence level of the extracted fact.",
    )
    retrieved_at: str = Field(..., description="ISO timestamp when fact was captured.")
    category: Optional[str] = Field(
        default=None,
        description="Specification category (e.g. electrical, compute, interface, software).",
    )


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str = Field(..., description="Error code identifier.")
    provider: Optional[str] = Field(default=None, description="Provider that produced the error.")
    message: str = Field(..., description="Human-readable error explanation.")
    retryable: bool = Field(default=False, description="Whether the operation may be retried.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional context or diagnostics.")


class ProjectMeta(BaseModel):
    """Target project metadata summary."""

    title: str
    domain: Optional[str] = None


class WebResearchAgentOutput(BaseModel):
    """Structured output contract for WebResearchAgent."""

    status: str = Field(default="success", description="'success' or 'error'.")
    project: ProjectMeta = Field(..., description="Target project metadata.")
    queries_used: List[str] = Field(default_factory=list, description="Search queries executed.")
    sources_found: int = Field(default=0, description="Total raw candidate sources discovered.")
    sources_selected: int = Field(default=0, description="Count of final ranked sources returned.")
    sources: List[NormalizedWebSource] = Field(default_factory=list, description="Ranked list of web sources.")
    facts: List[ExtractedEngineeringFact] = Field(
        default_factory=list,
        description="Structured engineering facts with provenance.",
    )
    errors: List[StructuredError] = Field(default_factory=list, description="List of errors encountered.")
