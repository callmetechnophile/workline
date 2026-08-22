"""Pydantic models and enums for secure team invitations and audit trail."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class InvitationStatus(str, Enum):
    """Lifecycle status of a team invitation."""
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    EXHAUSTED = "EXHAUSTED"
    ACCEPTED = "ACCEPTED"


class InvitationType(str, Enum):
    """Usage policy for invitation."""
    SINGLE_USE = "SINGLE_USE"
    MULTI_USE = "MULTI_USE"


class TeamRole(str, Enum):
    """Team member roles and permission tiers."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    VIEWER = "VIEWER"
    MEMBER = "MEMBER"


class AuditEventType(str, Enum):
    """Audit event identifiers for team invitation actions."""
    TEAM_INVITATION_CREATED = "TEAM_INVITATION_CREATED"
    TEAM_INVITATION_VIEWED = "TEAM_INVITATION_VIEWED"
    TEAM_INVITATION_ACCEPTED = "TEAM_INVITATION_ACCEPTED"
    TEAM_INVITATION_REVOKED = "TEAM_INVITATION_REVOKED"
    TEAM_INVITATION_EXPIRED = "TEAM_INVITATION_EXPIRED"
    TEAM_INVITATION_EXHAUSTED = "TEAM_INVITATION_EXHAUSTED"
    TEAM_INVITATION_REGENERATED = "TEAM_INVITATION_REGENERATED"


class InvitationPayload(BaseModel):
    """
    Minimum payload embedded inside authenticated encrypted token.
    Never contains emails, passwords, credentials, or private secrets.
    """
    invitation_id: str
    team_id: str
    issued_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    key_version: str = "v1"


class TeamInvitation(BaseModel):
    """
    Server-side database record stored in SurrealDB / SQLite.
    Stores token_hash instead of plaintext token.
    """
    invitation_id: str
    team_id: str
    created_by: str = "system"
    token_hash: str
    status: InvitationStatus = InvitationStatus.ACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str
    max_uses: int = 10
    use_count: int = 0
    accepted_by: List[str] = Field(default_factory=list)
    accepted_at: Optional[str] = None
    revoked_at: Optional[str] = None
    key_version: str = "v1"
    role: str = "MEMBER"


class CreateInvitationRequest(BaseModel):
    """Request schema for generating a team invitation link."""
    team_id: str
    created_by: str = "system"
    ttl_days: int = 7
    max_uses: int = 10
    role: str = "MEMBER"


class CreateInvitationResponse(BaseModel):
    """Response returned upon generating a secure invitation."""
    invitation_id: str
    team_id: str
    join_url: str
    expires_at: str
    max_uses: int
    status: InvitationStatus
    message_template: str


class InvitationPreview(BaseModel):
    """Safe pre-join preview data shown after token validation."""
    valid: bool
    team_name: str
    team_id: str
    member_count: int
    invited_by: str
    expires_at: str
    status: str
    role: str


class AcceptInvitationRequest(BaseModel):
    """Request payload when authenticated user accepts an invitation."""
    user_id: str
    user_name: Optional[str] = None


class AcceptInvitationResponse(BaseModel):
    """Result of accepting a team invitation."""
    success: bool
    team_id: str
    team_name: str
    role: str
    message: str


class InvitationAuditEvent(BaseModel):
    """Immutable audit record for team invitation actions."""
    event_id: str
    event_type: AuditEventType
    team_id: str
    invitation_id: str
    user_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)
