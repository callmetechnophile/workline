"""
Workline AI — Team Collaboration Data Models and Enums.

Strict Security Invariant:
Plaintext join codes are NEVER stored in Team database models.
Only HMAC-SHA-256 digests (`join_code_digest`) are persisted.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TeamRole(str, Enum):
    """Team membership roles."""
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class TeamStatus(str, Enum):
    """Lifecycle status of a team."""
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    SUSPENDED = "SUSPENDED"


class TeamMemberStatus(str, Enum):
    """Lifecycle status of a member in a team."""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REMOVED = "REMOVED"


class TeamAuditEventType(str, Enum):
    """Auditable team events."""
    TEAM_CREATED = "TEAM_CREATED"
    MEMBER_JOINED = "MEMBER_JOINED"
    MEMBER_REMOVED = "MEMBER_REMOVED"
    MEMBER_ROLE_CHANGED = "MEMBER_ROLE_CHANGED"
    JOIN_CODE_CREATED = "JOIN_CODE_CREATED"
    JOIN_CODE_ROTATED = "JOIN_CODE_ROTATED"
    JOIN_CODE_REVOKED = "JOIN_CODE_REVOKED"
    JOIN_ATTEMPT_FAILED = "JOIN_ATTEMPT_FAILED"
    JOIN_ATTEMPT_RATE_LIMITED = "JOIN_ATTEMPT_RATE_LIMITED"


class Team(BaseModel):
    """Team entity. Stores only join_code_digest, never plaintext join codes."""
    id: str
    name: str
    description: Optional[str] = ""
    owner_id: str
    join_code_digest: Optional[str] = None
    join_code_created_at: Optional[str] = None
    join_code_expires_at: Optional[str] = None
    join_code_enabled: bool = True
    status: TeamStatus = TeamStatus.ACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    member_count: int = 1


class TeamMember(BaseModel):
    """Individual member attached to a team. Unique by (team_id, user_id)."""
    id: str
    team_id: str
    user_id: str
    role: TeamRole = TeamRole.MEMBER
    status: TeamMemberStatus = TeamMemberStatus.ACTIVE
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TeamAuditEvent(BaseModel):
    """Immutable audit record. Never contains plaintext join codes or credentials."""
    event_id: str
    team_id: str
    actor_user_id: str
    target_user_id: Optional[str] = None
    event_type: TeamAuditEventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


# API Request/Response Models

class CreateTeamRequest(BaseModel):
    """Payload to create a new team."""
    name: str
    description: Optional[str] = ""


class CreateTeamResponse(BaseModel):
    """Response returned upon team creation. Returns plaintext join_code once."""
    team_id: str
    name: str
    description: Optional[str] = ""
    owner_id: str
    role: TeamRole = TeamRole.OWNER
    join_code: str
    join_code_expires_at: str
    message: str = "Team created successfully. Share this 6-character code with trusted collaborators."


class JoinTeamRequest(BaseModel):
    """Payload to join an existing team via 6-character code."""
    code: str


class JoinTeamResponse(BaseModel):
    """Result of joining a team."""
    status: str
    team_id: str
    team_name: str
    role: TeamRole
    message: str


class RotateJoinCodeResponse(BaseModel):
    """Result of rotating a join code. Returns new plaintext code once."""
    team_id: str
    join_code: str
    expires_at: str
    message: str = "Join code successfully rotated. Previous join code is now permanently revoked."


class RevokeJoinCodeResponse(BaseModel):
    """Result of revoking a join code."""
    team_id: str
    status: str = "REVOKED"
    message: str = "Join code successfully revoked."


class UpdateMemberRoleRequest(BaseModel):
    """Payload to update member role."""
    role: TeamRole
