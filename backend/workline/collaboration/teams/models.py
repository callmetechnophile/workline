"""
Workline AI — Team Collaboration Data Models, Roles, and Schemas.

Strict Security Invariant:
Plaintext join codes are NEVER stored in Team database models.
Only HMAC-SHA-256 digests (`join_code_digest`) are persisted.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TeamRole(str, Enum):
    """
    5-tier team membership roles with explicit capabilities:
    - OWNER: Full authority, member management, sole owner protection, ownership transfer.
    - ADMIN: Member management, joining code controls, artifact management.
    - ENGINEER: Modify artifacts (BOM, schematics, analysis), tasks, comments.
    - RESEARCHER: Read/write research, knowledge base, datasheets, research tasks.
    - VIEWER: Read-only access, comments where permitted.
    - MEMBER: Backward-compatibility alias for baseline member.
    """
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    RESEARCHER = "RESEARCHER"
    VIEWER = "VIEWER"
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


class MembershipRequestStatus(str, Enum):
    """Lifecycle states of a join request requiring approval."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


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
    MEMBERSHIP_REQUEST_CREATED = "MEMBERSHIP_REQUEST_CREATED"
    MEMBERSHIP_REQUEST_APPROVED = "MEMBERSHIP_REQUEST_APPROVED"
    MEMBERSHIP_REQUEST_REJECTED = "MEMBERSHIP_REQUEST_REJECTED"
    OWNERSHIP_TRANSFERRED = "OWNERSHIP_TRANSFERRED"
    TEAM_SETTINGS_UPDATED = "TEAM_SETTINGS_UPDATED"


class Team(BaseModel):
    """Team entity. Stores only join_code_digest, never plaintext join codes."""
    id: str
    name: str
    description: Optional[str] = ""
    project_id: Optional[str] = None
    owner_id: str
    join_code_digest: Optional[str] = None
    join_code_created_at: Optional[str] = None
    join_code_expires_at: Optional[str] = None
    join_code_enabled: bool = True
    require_join_approval: bool = False
    default_join_role: TeamRole = TeamRole.MEMBER
    status: TeamStatus = TeamStatus.ACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    member_count: int = 1


class TeamMember(BaseModel):
    """Individual member attached to a team. Unique by (team_id, user_id)."""
    id: str
    team_id: str
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    role: TeamRole = TeamRole.ENGINEER
    status: TeamMemberStatus = TeamMemberStatus.ACTIVE
    joined_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MembershipRequest(BaseModel):
    """Join request requiring administrative approval."""
    id: str
    team_id: str
    project_id: Optional[str] = None
    user_id: str
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    requested_role: TeamRole = TeamRole.ENGINEER
    status: MembershipRequestStatus = MembershipRequestStatus.PENDING
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    rejection_reason: Optional[str] = None


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
    project_id: Optional[str] = None
    require_join_approval: Optional[bool] = False
    default_join_role: Optional[TeamRole] = TeamRole.ENGINEER


class CreateTeamResponse(BaseModel):
    """Response returned upon team creation. Returns plaintext join_code once."""
    team_id: str
    name: str
    description: Optional[str] = ""
    project_id: Optional[str] = None
    owner_id: str
    role: TeamRole = TeamRole.OWNER
    join_code: str
    join_code_expires_at: str
    require_join_approval: bool = False
    message: str = "Team created successfully. Share this WL-XXXXXX join code with trusted collaborators."


class JoinTeamRequest(BaseModel):
    """Payload to join an existing team via 6-character code."""
    code: str
    requested_role: Optional[TeamRole] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class TeamPreviewResponse(BaseModel):
    """Safe metadata preview returned for a join code without joining."""
    team_id: str
    team_name: str
    description: Optional[str] = ""
    project_id: Optional[str] = None
    member_count: int
    require_join_approval: bool
    default_join_role: TeamRole
    allowed_roles: List[TeamRole]


class JoinTeamResponse(BaseModel):
    """Result of joining or requesting to join a team."""
    status: str  # JOINED, PENDING_APPROVAL, ALREADY_MEMBER
    team_id: str
    team_name: str
    role: Optional[TeamRole] = None
    request_id: Optional[str] = None
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


class ReviewMembershipRequest(BaseModel):
    """Payload to approve or reject a pending membership request."""
    action: str  # APPROVE or REJECT
    assigned_role: Optional[TeamRole] = None
    reason: Optional[str] = None


class TransferOwnershipRequest(BaseModel):
    """Payload to securely transfer team ownership."""
    target_user_id: str
    confirmation_phrase: str


class UpdateTeamSettingsRequest(BaseModel):
    """Payload to update team settings."""
    name: Optional[str] = None
    description: Optional[str] = None
    require_join_approval: Optional[bool] = None
    default_join_role: Optional[TeamRole] = None
