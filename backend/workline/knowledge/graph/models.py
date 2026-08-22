"""Data models and enums for the Engineering Knowledge Graph."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    PROJECT = "PROJECT"
    TEAM = "TEAM"
    DOCUMENT = "DOCUMENT"
    SECTION = "SECTION"
    COMPONENT = "COMPONENT"
    PART_NUMBER = "PART_NUMBER"
    MANUFACTURER = "MANUFACTURER"
    DATASHEET = "DATASHEET"
    SPECIFICATION = "SPECIFICATION"
    REQUIREMENT = "REQUIREMENT"
    DECISION = "DECISION"
    BOM_ITEM = "BOM_ITEM"
    PROCUREMENT_ITEM = "PROCUREMENT_ITEM"
    PROTOCOL = "PROTOCOL"
    INTERFACE = "INTERFACE"
    SENSOR = "SENSOR"
    ACTUATOR = "ACTUATOR"
    MATERIAL = "MATERIAL"
    TOOL = "TOOL"
    SOFTWARE = "SOFTWARE"
    DATASET = "DATASET"
    MODEL = "MODEL"
    ALGORITHM = "ALGORITHM"
    STANDARD = "STANDARD"
    RESEARCH_CONCEPT = "RESEARCH_CONCEPT"


class EntityStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUPERSEDED = "SUPERSEDED"
    UNRESOLVED = "UNRESOLVED"
    CONFLICTED = "CONFLICTED"
    DEPRECATED = "DEPRECATED"


class CanonicalEntity(BaseModel):
    entity_id: str
    entity_type: EntityType
    canonical_name: str
    aliases: List[str] = Field(default_factory=list)
    normalized_name: str
    project_id: str
    team_id: str = "default_team"
    status: EntityStatus = EntityStatus.ACTIVE
    confidence: float = 1.0
    manufacturer: Optional[str] = None
    base_part_number: Optional[str] = None
    package_variant: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityMention(BaseModel):
    mention_id: str
    document_id: str
    page_number: int = 1
    section_id: str = "general"
    entity_type: EntityType
    original_text: str
    normalized_text: str
    source_span: str
    confidence: float = 0.95
    context_hints: Dict[str, Any] = Field(default_factory=dict)


class Specification(BaseModel):
    specification_id: str
    entity_id: str
    property: str
    value: str
    normalized_value: float
    unit: str
    source_document: str
    page: int = 1
    section: str = "General"
    confidence: float = 0.95
    valid_from: Optional[float] = None
    valid_until: Optional[float] = None
    status: EntityStatus = EntityStatus.ACTIVE


class SpecificationConflict(BaseModel):
    conflict_id: str
    entity_id: str
    property: str
    value_a: str
    source_a: str
    value_b: str
    source_b: str
    status: str = "OPEN"
    created_at: float = Field(default_factory=time.time)


class RelationshipType(str, Enum):
    # Project
    HAS_REQUIREMENT = "HAS_REQUIREMENT"
    HAS_COMPONENT = "HAS_COMPONENT"
    HAS_BOM_ITEM = "HAS_BOM_ITEM"
    HAS_DECISION = "HAS_DECISION"
    HAS_DOCUMENT = "HAS_DOCUMENT"

    # Document
    MENTIONS = "MENTIONS"
    REFERENCES = "REFERENCES"
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"

    # Component
    MANUFACTURED_BY = "MANUFACTURED_BY"
    HAS_PART_NUMBER = "HAS_PART_NUMBER"
    HAS_DATASHEET = "HAS_DATASHEET"
    HAS_SPECIFICATION = "HAS_SPECIFICATION"
    HAS_ALIAS = "HAS_ALIAS"
    USED_IN = "USED_IN"

    # BOM
    REFERENCES_COMPONENT = "REFERENCES_COMPONENT"
    HAS_PROCUREMENT_ITEM = "HAS_PROCUREMENT_ITEM"

    # Requirement
    SATISFIED_BY = "SATISFIED_BY"
    SUPPORTED_BY = "SUPPORTED_BY"

    # Decision
    SELECTS = "SELECTS"
    REJECTS = "REJECTS"
    CONTRADICTED_BY = "CONTRADICTED_BY"

    # Procurement
    REPRESENTS = "REPRESENTS"
    SOLD_BY = "SOLD_BY"


class EngineeringRelationship(BaseModel):
    relationship_id: str
    project_id: str
    from_entity: str
    relationship_type: RelationshipType
    to_entity: str
    confidence: float = 1.0
    source_type: str = "PROJECT_STATE"
    source_document: Optional[str] = None
    source_span: Optional[str] = None
    created_at: float = Field(default_factory=time.time)
    status: str = "ACTIVE"
