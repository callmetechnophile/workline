"""
Pydantic data models for verified Evidence and Retrieval results.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Verified evidence item derived from documents, vector embeddings, or graph."""
    evidence_id: str = Field(default_factory=lambda: f"evi_{uuid.uuid4().hex[:10]}")
    source_type: str = Field(description="'document', 'spec', 'graph_node', 'supplier_catalog'")
    title: str
    snippet: str
    relevance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    source_uri_or_id: str
    verified: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RetrievalQuery(BaseModel):
    """Structured query for knowledge and evidence discovery."""
    query: str
    project_id: Optional[str] = None
    top_k: int = 5
    source_filters: Optional[List[str]] = None
    min_relevance: float = 0.5


class RetrievalResult(BaseModel):
    """Aggregated retrieval bundle with citations."""
    query: str
    evidence_items: List[Evidence] = Field(default_factory=list)
    total_found: int = 0
