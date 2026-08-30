"""
Data contracts and Pydantic schemas for ResearchPaperAgent (Agent #1).
Defines structured input, normalized paper representations, errors, and A2A preparation models.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "ResearchPaperAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None


class ResearchPaperAgentInput(BaseModel):
    """Structured input contract for ResearchPaperAgent."""

    project_title: str = Field(
        ...,
        description="The title or core concept of the engineering project.",
        min_length=1,
    )
    project_description: str = Field(
        ...,
        description="Detailed description of the engineering goal, system, and architecture.",
        min_length=1,
    )
    engineering_domain: Optional[str] = Field(
        default=None,
        description="Discipline or domain (e.g. Robotics, Power Electronics, Embedded Systems).",
    )
    research_objectives: List[str] = Field(
        default_factory=list,
        description="Specific research questions or technical topics to investigate.",
    )
    components: List[str] = Field(
        default_factory=list,
        description="Hardware/software components (e.g. Jetson Orin Nano, Pixhawk 6C).",
    )
    technologies: List[str] = Field(
        default_factory=list,
        description="Algorithms, frameworks, or protocols (e.g. YOLOv8, CAN bus, DShot).",
    )
    constraints: List[str] = Field(
        default_factory=list,
        description="Engineering constraints (e.g. real-time, low-power, thermal limit).",
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="Target search keywords and domain terminology.",
    )
    max_papers: int = Field(
        default=20,
        description="Maximum number of candidate papers to return (default 20, max 50).",
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


class RawPaperRecord(BaseModel):
    """Raw candidate record returned by the Freephdlabor provider."""

    paper_id: Optional[str] = None
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    venue: Optional[str] = None
    paper_url: Optional[str] = None
    pdf_url: Optional[str] = None
    citation_count: Optional[int] = None
    keywords: List[str] = Field(default_factory=list)
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class NormalizedPaper(BaseModel):
    """Normalized, deduplicated, and relevance-scored research paper representation."""

    paper_id: str = Field(..., description="Unique paper identifier or hash.")
    title: str = Field(..., description="Academic paper title.")
    authors: List[str] = Field(default_factory=list, description="List of paper authors.")
    abstract: Optional[str] = Field(default=None, description="Paper abstract text.")
    publication_date: Optional[str] = Field(default=None, description="ISO date or publication year.")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier.")
    venue: Optional[str] = Field(default=None, description="Journal or conference name.")
    source: str = Field(default="freephdlabor", description="Acquisition provider source.")
    paper_url: Optional[str] = Field(default=None, description="Canonical paper web URL.")
    pdf_url: Optional[str] = Field(default=None, description="Direct URL to PDF file if available.")
    pdf_available: bool = Field(default=False, description="True if a valid PDF URL exists.")
    citation_count: Optional[int] = Field(default=None, description="Citation count if provided by source.")
    keywords: List[str] = Field(default_factory=list, description="Extracted or source keywords.")
    relevance_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Relevance score between 0.0 and 1.0.",
    )
    relevance_reasons: List[str] = Field(
        default_factory=list,
        description="Transparent explanations for the assigned relevance score.",
    )


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str = Field(..., description="Error code identifier (e.g. PROVIDER_RATE_LIMIT).")
    message: str = Field(..., description="Human-readable error explanation.")
    retryable: bool = Field(default=False, description="Whether the operation may be retried.")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional context or diagnostics.")


class ProjectMeta(BaseModel):
    """Summary of the target project context."""

    title: str
    domain: Optional[str] = None


class ResearchPaperAgentOutput(BaseModel):
    """Structured output contract for ResearchPaperAgent."""

    status: str = Field(default="success", description="'success' or 'error'.")
    project: ProjectMeta = Field(..., description="Target project metadata.")
    queries_used: List[str] = Field(default_factory=list, description="Search queries generated and executed.")
    papers_found: int = Field(default=0, description="Total raw candidate papers retrieved prior to deduplication.")
    papers_selected: int = Field(default=0, description="Count of final ranked papers returned.")
    papers: List[NormalizedPaper] = Field(default_factory=list, description="Ranked list of normalized papers.")
    errors: List[StructuredError] = Field(default_factory=list, description="List of any errors encountered.")
