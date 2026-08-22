"""Data models and enums for the Document Intelligence Pipeline."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SourceType(str, Enum):
    UPLOAD = "UPLOAD"
    PDF = "PDF"
    DATASHEET = "DATASHEET"
    RESEARCH_PAPER = "RESEARCH_PAPER"
    WEB = "WEB"
    GITHUB = "GITHUB"
    GIT = "GIT"
    WLIPJT = "WLIPJT"
    GENERATED = "GENERATED"
    OTHER = "OTHER"


class DocumentStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    INGESTING = "INGESTING"
    PARSED = "PARSED"
    ENRICHED = "ENRICHED"
    INDEXED = "INDEXED"
    FAILED = "FAILED"
    STALE = "STALE"


class EngineeringEntityType(str, Enum):
    COMPONENT = "COMPONENT"
    MANUFACTURER = "MANUFACTURER"
    MODEL_NUMBER = "MODEL_NUMBER"
    PART_NUMBER = "PART_NUMBER"
    VOLTAGE = "VOLTAGE"
    CURRENT = "CURRENT"
    POWER = "POWER"
    RESISTANCE = "RESISTANCE"
    CAPACITANCE = "CAPACITANCE"
    INDUCTANCE = "INDUCTANCE"
    FREQUENCY = "FREQUENCY"
    TEMPERATURE = "TEMPERATURE"
    PACKAGE = "PACKAGE"
    PROTOCOL = "PROTOCOL"
    INTERFACE = "INTERFACE"
    MATERIAL = "MATERIAL"
    DIMENSION = "DIMENSION"
    UNIT = "UNIT"
    STANDARD = "STANDARD"
    TOOL = "TOOL"
    SOFTWARE = "SOFTWARE"
    DATASET = "DATASET"
    MODEL = "MODEL"
    ALGORITHM = "ALGORITHM"


class EngineeringEntity(BaseModel):
    entity_id: str
    project_id: str
    document_id: str
    entity_type: EngineeringEntityType
    original_text: str
    normalized_value: str
    unit: Optional[str] = None
    page_number: int = 1
    section: str = "General"
    confidence: float = 0.95
    source_span: str = ""
    created_at: float = Field(default_factory=time.time)


class TableElement(BaseModel):
    table_id: str
    document_id: str
    page_number: int = 1
    section_title: str = "General"
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    caption: Optional[str] = None


class FigureElement(BaseModel):
    figure_id: str
    document_id: str
    page_number: int = 1
    section_title: str = "General"
    caption: Optional[str] = None
    artifact_reference: Optional[str] = None


class SectionElement(BaseModel):
    section_id: str
    heading: str
    level: int = 1
    page_number: int = 1
    paragraphs: List[str] = Field(default_factory=list)
    tables: List[TableElement] = Field(default_factory=list)
    figures: List[FigureElement] = Field(default_factory=list)


class DocumentRecord(BaseModel):
    document_id: str
    project_id: str
    team_id: str = "default_team"
    source_type: SourceType = SourceType.DATASHEET
    source_uri: str = ""
    filename: str
    mime_type: str = "application/pdf"
    title: str
    source_hash: str
    content_hash: str
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    parser: str = "DoclingParser"
    parser_version: str = "2.1.0"
    status: DocumentStatus = DocumentStatus.DISCOVERED
    sections: List[SectionElement] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
