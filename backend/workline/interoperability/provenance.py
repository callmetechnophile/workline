"""Task provenance and execution tracking for external agent invocations."""

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


def compute_sha256(data: Any) -> str:
    """Compute deterministic SHA-256 hash of structured or scalar data."""
    if isinstance(data, str):
        content = data.encode("utf-8")
    elif isinstance(data, bytes):
        content = data
    else:
        content = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(content).hexdigest()


class TaskProvenance(BaseModel):
    """Immutable provenance record tracking who generated what, when, and how."""
    task_id: str
    agent_id: str
    agent_version: str
    capability: str
    protocol: str
    input_hash: str
    output_hash: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    execution_duration: float = Field(default=0.0, description="Duration in seconds")
    endpoint: Optional[str] = None
    provider: Optional[str] = None
