"""Embedding provenance tracking and content hash calculations."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EmbeddingProvenance(BaseModel):
    """Metadata tracking embedding model provenance for incremental updates and re-indexing."""
    object_id: str
    object_type: str
    project_id: str
    embedding_model: str = "workline-local-384"
    embedding_dimension: int = 384
    source_hash: str
    indexed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


def compute_content_hash(content: str) -> str:
    """Computes a SHA-256 digest of normalized text content."""
    normalized = " ".join(content.strip().lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
