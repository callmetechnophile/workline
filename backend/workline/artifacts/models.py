"""
Pydantic data models for file and binary artifact management.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Artifact(BaseModel):
    """Metadata record for a binary or structured artifact."""
    artifact_id: str = Field(default_factory=lambda: f"art_{uuid.uuid4().hex[:12]}")
    project_id: Optional[str] = None
    job_id: Optional[str] = None
    filename: str
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    sha256_hash: Optional[str] = None
    storage_backend: str = "filesystem"  # or 's3'
    storage_path_or_uri: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
