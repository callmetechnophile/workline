"""
Data contracts and Pydantic schemas for DocumentProcessingAgent (Agent #3).
Defines structured input, extracted sections, tables, figures, links, semantic chunks,
engineering facts with character/page provenance, and quality metrics.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


DocumentTypeLiteral = Literal["pdf", "html", "text", "auto"]
BlockTypeLiteral = Literal["paragraph", "heading", "table", "code", "figure_caption", "list_item"]
TableStatusLiteral = Literal["success", "table_extraction_failed"]


class RequestContext(BaseModel):
    """Execution and governance context for ArmorIQ / A2A integration."""

    user_id: Optional[str] = None
    project_id: Optional[str] = None
    agent_id: str = "DocumentProcessingAgent"
    parent_agent_id: Optional[str] = None
    authorization_context: Optional[Dict[str, Any]] = None
    execution_id: Optional[str] = None
    tool_scope: List[str] = Field(default_factory=list)


class DocumentProcessingInput(BaseModel):
    """Structured input contract for DocumentProcessingAgent."""

    document_id: str = Field(
        ...,
        description="Unique identifier for the document or paper.",
        min_length=1,
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Remote URL to download PDF, HTML, or text document.",
    )
    local_path: Optional[str] = Field(
        default=None,
        description="Local filesystem path to document file.",
    )
    document_type: DocumentTypeLiteral = Field(
        default="auto",
        description="Format type: 'pdf', 'html', 'text', or 'auto' (detected from extension/content).",
    )
    title: Optional[str] = Field(
        default=None,
        description="Optional pre-known title of the document.",
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Project identifier.",
    )
    source_agent: Optional[str] = Field(
        default=None,
        description="Originating upstream agent ('research_paper_agent' | 'web_research_agent').",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional auxiliary metadata passed from upstream.",
    )
    request_context: Optional[RequestContext] = Field(
        default=None,
        description="ArmorIQ / A2A execution context.",
    )

    @model_validator(mode="after")
    def validate_source_exists(self) -> "DocumentProcessingInput":
        if not self.source_url and not self.local_path:
            raise ValueError("At least one of 'source_url' or 'local_path' must be provided.")
        return self


class DocumentMetadata(BaseModel):
    """Comprehensive document metadata model."""

    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    journal: Optional[str] = None
    conference: Optional[str] = None
    doi: Optional[str] = None
    isbn: Optional[str] = None
    url: Optional[str] = None
    pdf_url: Optional[str] = None
    language: Optional[str] = "en"
    page_count: int = Field(default=1, ge=1)
    document_type: str = "pdf"
    file_size_bytes: Optional[int] = None
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None


class ExtractedBlock(BaseModel):
    """Extracted text block with strict character and page provenance."""

    block_id: str
    page_number: int = Field(..., ge=1, description="1-indexed document page number.")
    section_title: str = "Introduction"
    text: str
    block_type: BlockTypeLiteral = "paragraph"
    character_start: int = Field(default=0, ge=0)
    character_end: int = Field(default=0, ge=0)
    source_url: Optional[str] = None


class ExtractedSection(BaseModel):
    """Structured hierarchical section."""

    section_title: str
    level: int = Field(default=2, ge=1, le=4)
    page_start: int = Field(default=1, ge=1)
    page_end: int = Field(default=1, ge=1)
    text: str
    blocks: List[ExtractedBlock] = Field(default_factory=list)


class ExtractedTable(BaseModel):
    """Extracted tabular dataset."""

    table_id: str
    page_number: int = Field(default=1, ge=1)
    caption: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    markdown: str = ""
    extraction_status: TableStatusLiteral = "success"


class ExtractedFigure(BaseModel):
    """Extracted figure and caption reference."""

    figure_number: Optional[str] = None
    caption: str
    page_number: int = Field(default=1, ge=1)
    bounding_box: Optional[List[float]] = None


class ExtractedLink(BaseModel):
    """Extracted hyperlinked reference."""

    text: str
    url: str
    link_type: str = "web"  # "doi", "github", "manufacturer", "pdf", "web"
    page_number: int = Field(default=1, ge=1)


class ExtractedReference(BaseModel):
    """Academic bibliography or reference item."""

    reference_id: str
    raw_text: str
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None


class DocumentChunk(BaseModel):
    """Semantic document chunk with section and page bounding."""

    chunk_id: str
    document_id: str
    text: str
    section: str
    page_start: int = Field(default=1, ge=1)
    page_end: int = Field(default=1, ge=1)
    source_url: Optional[str] = None
    character_start: int = 0
    character_end: int = 0
    token_estimate: int = 0


class EngineeringEntity(BaseModel):
    """Extracted engineering hardware/software entity."""

    name: str
    category: str  # microcontroller, sensor, actuator, protocol, interface, power_system, algorithm
    page_number: int = 1
    context_snippet: Optional[str] = None
    candidate_relationship: Optional[str] = None


class EngineeringFact(BaseModel):
    """Extracted technical factual statement with provenance."""

    fact: str
    entity: Optional[str] = None
    attribute: Optional[str] = None
    value: Optional[str] = None
    normalized_value: Optional[float] = None
    normalized_unit: Optional[str] = None
    source_document: str
    page: int = 1
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class StructuredError(BaseModel):
    """Machine-readable structured error model."""

    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class DocumentProcessingOutput(BaseModel):
    """Structured output contract for DocumentProcessingAgent."""

    status: Literal["success", "ocr_required", "error"] = "success"
    document_id: str
    metadata: DocumentMetadata
    markdown: str = ""
    sections: List[ExtractedSection] = Field(default_factory=list)
    tables: List[ExtractedTable] = Field(default_factory=list)
    figures: List[ExtractedFigure] = Field(default_factory=list)
    links: List[ExtractedLink] = Field(default_factory=list)
    references: List[ExtractedReference] = Field(default_factory=list)
    chunks: List[DocumentChunk] = Field(default_factory=list)
    entities: List[EngineeringEntity] = Field(default_factory=list)
    facts: List[EngineeringFact] = Field(default_factory=list)
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    quality_warnings: List[str] = Field(default_factory=list)
    errors: List[StructuredError] = Field(default_factory=list)
