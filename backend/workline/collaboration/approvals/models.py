"""
Workline AI — Sensitive Approvals Queue Models.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """Lifecycle states of an approval request."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApprovalRequest(BaseModel):
    """Approval request for sensitive engineering operations."""
    id: str = Field(default_factory=lambda: f"APPR-{uuid.uuid4().hex[:8].upper()}")
    project_id: str
    team_id: Optional[str] = None
    requester_id: str
    requester_name: Optional[str] = None
    approver_id: Optional[str] = None
    approver_name: Optional[str] = None
    artifact_type: str  # "BOM_CHANGE", "ARCHITECTURE_DECISION", "COMPONENT_SUBSTITUTION", "RELEASE_GATE", "AGENT_MUTATION"
    artifact_id: str
    action: str  # Description of action requested
    reason: Optional[str] = ""
    diff_summary: Optional[str] = None  # e.g., "MPU6050 -> BMI270 (Stock deficit)"
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: Optional[str] = None
    resolution_notes: Optional[str] = None


class CreateApprovalRequest(BaseModel):
    """Payload to submit an action for administrative approval."""
    project_id: str
    team_id: Optional[str] = None
    artifact_type: str
    artifact_id: str
    action: str
    reason: Optional[str] = ""
    diff_summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ResolveApprovalRequest(BaseModel):
    """Payload to approve or reject a request."""
    status: ApprovalStatus  # APPROVED or REJECTED
    notes: Optional[str] = None
