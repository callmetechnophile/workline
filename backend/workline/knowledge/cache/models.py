"""Python data models and enums for the Knowledge Cache layer."""

from enum import Enum
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CacheObjectType(str, Enum):
    """Categorized cache entry types."""
    DOCUMENT_PARSE = "DOCUMENT_PARSE"
    DOCUMENT_CHUNK = "DOCUMENT_CHUNK"
    EMBEDDING = "EMBEDDING"
    RETRIEVAL = "RETRIEVAL"
    CONTEXT = "CONTEXT"
    SUMMARY = "SUMMARY"
    RESEARCH = "RESEARCH"
    AGENT_DISCOVERY = "AGENT_DISCOVERY"


class CacheOptions(BaseModel):
    """Configuration options when storing cache items."""
    ttl: Optional[int] = None
    project_id: str
    team_id: str = "default_team"
    source_id: Optional[str] = None
    source_hash: Optional[str] = None
    schema_version: str = "1.0.0"
    project_version: Optional[str] = None
    git_commit: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    embedding_dimension: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CacheMetadata(BaseModel):
    """Header metadata for every cached object."""
    cache_key: str
    object_type: CacheObjectType
    project_id: str
    team_id: str = "default_team"
    source_id: Optional[str] = None
    source_hash: Optional[str] = None
    schema_version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)
    expires_at: float = 0.0
    project_version: Optional[str] = None
    git_commit: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    embedding_dimension: Optional[int] = None
    size_bytes: int = 0


class CacheStats(BaseModel):
    """Observability metrics and cache hit/miss statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expired: int = 0
    invalidations: int = 0
    l1_entries: int = 0
    l2_entries: int = 0
    l2_size_bytes: int = 0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
