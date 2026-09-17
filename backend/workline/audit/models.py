"""
Pydantic data models for Immutable Append-Only Audit Trail.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Immutable audit record."""
    event_id: str = Field(default_factory=lambda: f"aud_{uuid.uuid4().hex[:12]}")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str  # e.g., 'action.recommendation', 'action.authorization', 'order.executed'
    actor_id: str
    actor_role: str
    project_id: Optional[str] = None
    correlation_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
