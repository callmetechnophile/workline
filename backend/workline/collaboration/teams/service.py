"""
Workline AI — Secure Team Collaboration & Join Code Service.

Provides:
1. Team lifecycle management (Create, Get, List, Archive, Settings).
2. Cryptographically secure 'WL-XXXXXX' CSPRNG join code generation with HMAC-SHA-256 storage.
3. Code rotation, revocation, and configurable TTL expiration.
4. Membership request & approval gate flow (require_join_approval).
5. Brute-force rate limiting and code enumeration protection (generic error responses).
6. Safe pre-join metadata preview.
7. Duplicate membership prevention.
8. 5-tier Role-Based Access Control (OWNER, ADMIN, ENGINEER, RESEARCHER, VIEWER).
9. Strict sole owner protection and formal ownership transfer protocol.
10. Project access authorization verification.
11. Complete audit logging with zero plaintext secrets or join codes.
"""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import re
import secrets
import string
import uuid
from typing import Any, Dict, List, Optional, Tuple
from loguru import logger

from backend.workline.collaboration.teams.models import (
    CreateTeamResponse,
    JoinTeamResponse,
    MembershipRequest,
    MembershipRequestStatus,
    RevokeJoinCodeResponse,
    RotateJoinCodeResponse,
    Team,
    TeamAuditEvent,
    TeamAuditEventType,
    TeamMember,
    TeamMemberStatus,
    TeamPreviewResponse,
    TeamRole,
    TeamStatus,
)
from backend.workline.collaboration.teams.rate_limiter import join_rate_limiter

# Unambiguous alphabet: excludes 0, O, 1, I to prevent human transcription errors
JOIN_CODE_PREFIX = "WL-"
JOIN_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
JOIN_CODE_LENGTH = 6
JOIN_CODE_REGEX = re.compile(r"^(?:WL-)?[2-9A-HJ-NP-Z]{6}$", re.IGNORECASE)
LEGACY_CODE_REGEX = re.compile(r"^[A-Z0-9]{6}$")
DEFAULT_JOIN_CODE_TTL_SECONDS = 604800  # 7 days


class TeamServiceError(Exception):
    """Base exception for team operations."""
    pass


class PermissionDeniedError(TeamServiceError):
    """Raised when user lacks required role/permission for a team action."""
    pass


class TeamNotFoundError(TeamServiceError):
    """Raised when team does not exist."""
    pass


class InvalidJoinCodeError(TeamServiceError):
    """Raised on invalid, expired, or non-existent join code (intentionally generic)."""
    pass


class RateLimitExceededError(TeamServiceError):
    """Raised when brute-force rate limit is triggered."""
    pass


class TeamService:
    """Core collaboration service managing teams, memberships, join codes, requests, and audit logs."""

    def __init__(self, hmac_secret: Optional[bytes] = None):
        self._hmac_secret = hmac_secret or self._load_hmac_secret()
        # In-memory stores (synced with database / persistence layer)
        self._teams: Dict[str, Team] = {}
        self._members: Dict[str, Dict[str, TeamMember]] = {}  # team_id -> {user_id: TeamMember}
        self._membership_requests: Dict[str, MembershipRequest] = {}  # request_id -> MembershipRequest
        self._audit_logs: List[TeamAuditEvent] = []
        self._project_teams: Dict[str, str] = {}  # project_id -> team_id

    def _load_hmac_secret(self) -> bytes:
        """Loads HMAC secret from environment variable or generates secure session secret."""
        raw_secret = os.getenv("TEAM_JOIN_CODE_SECRET")
        if raw_secret:
            return raw_secret.strip().encode("utf-8")
        return secrets.token_bytes(32)

    def _compute_code_digest(self, normalized_code: str) -> str:
        """Computes HMAC-SHA-256 digest of normalized join code."""
        return hmac.new(
            self._hmac_secret,
            normalized_code.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _generate_unique_join_code(self) -> Tuple[str, str]:
        """
        Generates a secure 'WL-XXXXXX' code using CSPRNG and unambiguous alphanumeric chars.
        Handles collisions by bounded retries.
        Returns: (plaintext_code, hmac_digest)
        """
        for _ in range(10):
            suffix = "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(JOIN_CODE_LENGTH))
            full_code = f"{JOIN_CODE_PREFIX}{suffix}"
            digest = self._compute_code_digest(full_code)

            # Ensure no active collision
            collision = any(
                t.join_code_digest == digest and t.join_code_enabled and t.status == TeamStatus.ACTIVE
                for t in self._teams.values()
            )
            if not collision:
                return full_code, digest

        raise RuntimeError("Failed to generate unique join code after 10 attempts.")

    def _get_ttl_seconds(self) -> int:
        """Reads configurable join code TTL from environment."""
        try:
            val = os.getenv("TEAM_JOIN_CODE_TTL_SECONDS")
            return int(val) if val else DEFAULT_JOIN_CODE_TTL_SECONDS
        except ValueError:
            return DEFAULT_JOIN_CODE_TTL_SECONDS

    def _record_audit_event(
        self,
        team_id: str,
        actor_user_id: str,
        event_type: TeamAuditEventType,
        target_user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Records an immutable audit event without plaintext join codes."""
        event = TeamAuditEvent(
            event_id=f"audit_{uuid.uuid4().hex[:12]}",
            team_id=team_id,
            actor_user_id=actor_user_id,
            target_user_id=target_user_id,
            event_type=event_type,
            request_id=request_id,
            metadata=metadata or {},
        )
        self._audit_logs.append(event)
        logger.info(
            f"[TeamAudit] event={event_type.value} team_id={team_id} actor={actor_user_id} target={target_user_id}"
        )

    # -----------------------------------------------------------------------
    # Team Lifecycle
    # -----------------------------------------------------------------------

    def create_team(
        self,
        name: str,
        creator_user_id: str,
        description: str = "",
        project_id: Optional[str] = None,
        require_join_approval: bool = False,
        default_join_role: TeamRole = TeamRole.MEMBER,
        request_id: Optional[str] = None,
    ) -> CreateTeamResponse:
        """
        Creates a new team, designates creator as OWNER, and generates initial WL-XXXXXX join code.
        Returns plaintext join code ONCE to creator.
        """
        if not creator_user_id or not creator_user_id.strip():
            raise PermissionDeniedError("Authentication required to create a team.")

        clean_name = name.strip()
        if not clean_name:
            raise ValueError("Team name cannot be empty.")

        team_id = f"team_{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)
        ttl = self._get_ttl_seconds()
        expires_at = (now + timedelta(seconds=ttl)).isoformat()

        plaintext_code, digest = self._generate_unique_join_code()

        team = Team(
            id=team_id,
            name=clean_name,
            description=description.strip(),
            project_id=project_id,
            owner_id=creator_user_id,
            join_code_digest=digest,
            join_code_created_at=now.isoformat(),
            join_code_expires_at=expires_at,
            join_code_enabled=True,
            require_join_approval=require_join_approval,
            default_join_role=default_join_role,
            status=TeamStatus.ACTIVE,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            member_count=1,
        )
        self._teams[team_id] = team

        if project_id:
            self._project_teams[project_id] = team_id

        # Assign creator as OWNER
        member = TeamMember(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            team_id=team_id,
            user_id=creator_user_id,
            role=TeamRole.OWNER,
            status=TeamMemberStatus.ACTIVE,
            joined_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        self._members[team_id] = {creator_user_id: member}

        # Audit
        self._record_audit_event(
            team_id=team_id,
            actor_user_id=creator_user_id,
            event_type=TeamAuditEventType.TEAM_CREATED,
            request_id=request_id,
            metadata={"team_name": clean_name, "project_id": project_id},
        )
        self._record_audit_event(
            team_id=team_id,
            actor_user_id=creator_user_id,
            event_type=TeamAuditEventType.JOIN_CODE_CREATED,
            request_id=request_id,
            metadata={"expires_at": expires_at},
        )

        return CreateTeamResponse(
            team_id=team_id,
            name=team.name,
            description=team.description,
            project_id=team.project_id,
            owner_id=team.owner_id,
            role=TeamRole.OWNER,
            join_code=plaintext_code,
            join_code_expires_at=expires_at,
            require_join_approval=team.require_join_approval,
        )

    def get_team(self, team_id: str, actor_user_id: str) -> Team:
        """Retrieves team details if user is an active member or owner."""
        team = self._teams.get(team_id)
        if not team or team.status != TeamStatus.ACTIVE:
            raise TeamNotFoundError("Team not found.")

        # Membership verification
        members = self._members.get(team_id, {})
        if actor_user_id not in members or members[actor_user_id].status != TeamMemberStatus.ACTIVE:
            raise PermissionDeniedError("Access denied: You are not an active member of this team.")

        return team

    def list_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """Lists all active teams the user belongs to."""
        results = []
        for team_id, members in self._members.items():
            if user_id in members and members[user_id].status == TeamMemberStatus.ACTIVE:
                team = self._teams.get(team_id)
                if team and team.status == TeamStatus.ACTIVE:
                    results.append({
                        "team_id": team.id,
                        "name": team.name,
                        "description": team.description,
                        "project_id": team.project_id,
                        "role": members[user_id].role,
                        "member_count": team.member_count,
                        "require_join_approval": team.require_join_approval,
                        "created_at": team.created_at,
                    })
        return results

    def update_team_settings(
        self,
        team_id: str,
        actor_user_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        require_join_approval: Optional[bool] = None,
        default_join_role: Optional[TeamRole] = None,
        request_id: Optional[str] = None,
    ) -> Team:
        """Updates team settings. Allowed for OWNER and ADMIN."""
        team = self.get_team(team_id, actor_user_id)
        member = self._members[team_id][actor_user_id]
        if member.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only OWNER or ADMIN can update team settings.")

        if name is not None and name.strip():
            team.name = name.strip()
        if description is not None:
            team.description = description.strip()
        if require_join_approval is not None:
            team.require_join_approval = require_join_approval
        if default_join_role is not None:
            team.default_join_role = default_join_role

        team.updated_at = datetime.now(timezone.utc).isoformat()

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.TEAM_SETTINGS_UPDATED,
            request_id=request_id,
            metadata={
                "name": team.name,
                "require_join_approval": team.require_join_approval,
                "default_join_role": team.default_join_role.value,
            },
        )
        return team

    # -----------------------------------------------------------------------
    # Join Code Normalization & Lookup
    # -----------------------------------------------------------------------

    def _resolve_team_by_code(self, raw_code: str) -> Optional[Team]:
        """Resolves active team matching code digest supporting WL-XXXXXX and legacy 6-char formats."""
        if not raw_code:
            return None

        clean = raw_code.strip().upper()
        now = datetime.now(timezone.utc)

        # Build candidate normalization strings
        candidates = [clean]
        if clean.startswith(JOIN_CODE_PREFIX):
            candidates.append(clean[len(JOIN_CODE_PREFIX):])
        else:
            candidates.append(f"{JOIN_CODE_PREFIX}{clean}")

        candidate_digests = {self._compute_code_digest(c) for c in candidates}

        for team in self._teams.values():
            if (
                team.join_code_digest in candidate_digests
                and team.join_code_enabled
                and team.status == TeamStatus.ACTIVE
            ):
                if team.join_code_expires_at:
                    try:
                        exp = datetime.fromisoformat(team.join_code_expires_at)
                        if exp > now:
                            return team
                    except Exception:
                        pass
                else:
                    return team

        return None

    # -----------------------------------------------------------------------
    # Join Code Preview & Join Flow
    # -----------------------------------------------------------------------

    def preview_join_code(
        self,
        raw_code: str,
        client_ip: str = "unknown",
    ) -> TeamPreviewResponse:
        """
        Validates join code and returns safe pre-join team preview.
        Does not reveal secrets or create membership.
        """
        is_blocked, remaining = join_rate_limiter.is_rate_limited(client_ip)
        if is_blocked:
            raise RateLimitExceededError(
                f"Too many failed join attempts. Please wait {remaining} seconds before trying again."
            )

        team = self._resolve_team_by_code(raw_code)
        if not team:
            join_rate_limiter.record_attempt(client_ip, success=False)
            raise InvalidJoinCodeError("Invalid or expired team code.")

        join_rate_limiter.record_attempt(client_ip, success=True)
        return TeamPreviewResponse(
            team_id=team.id,
            team_name=team.name,
            description=team.description or "",
            project_id=team.project_id,
            member_count=team.member_count,
            require_join_approval=team.require_join_approval,
            default_join_role=team.default_join_role,
            allowed_roles=[TeamRole.ENGINEER, TeamRole.RESEARCHER, TeamRole.VIEWER],
        )

    def join_team(
        self,
        raw_code: str,
        user_id: str,
        requested_role: Optional[TeamRole] = None,
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
        client_ip: str = "unknown",
        request_id: Optional[str] = None,
    ) -> JoinTeamResponse:
        """
        Validates code, enforces rate limits, checks expiration, and joins or creates a membership request.
        """
        if not user_id or not user_id.strip():
            raise PermissionDeniedError("Authentication required to join a team.")

        # Rate limiting check
        is_blocked, remaining = join_rate_limiter.is_rate_limited(user_id)
        if not is_blocked:
            is_blocked, remaining = join_rate_limiter.is_rate_limited(client_ip)

        if is_blocked:
            self._record_audit_event(
                team_id="unknown",
                actor_user_id=user_id,
                event_type=TeamAuditEventType.JOIN_ATTEMPT_RATE_LIMITED,
                request_id=request_id,
                metadata={"client_ip": client_ip, "remaining_seconds": remaining},
            )
            raise RateLimitExceededError(
                f"Too many failed join attempts. Please wait {remaining} seconds before trying again."
            )

        matched_team = self._resolve_team_by_code(raw_code)
        if not matched_team:
            join_rate_limiter.record_attempt(user_id, success=False)
            join_rate_limiter.record_attempt(client_ip, success=False)
            self._record_audit_event(
                team_id="unknown",
                actor_user_id=user_id,
                event_type=TeamAuditEventType.JOIN_ATTEMPT_FAILED,
                request_id=request_id,
                metadata={"client_ip": client_ip},
            )
            raise InvalidJoinCodeError("Invalid or expired team code.")

        team_id = matched_team.id
        team_members = self._members.setdefault(team_id, {})
        now = datetime.now(timezone.utc)

        # Duplicate membership check
        if user_id in team_members and team_members[user_id].status == TeamMemberStatus.ACTIVE:
            join_rate_limiter.record_attempt(user_id, success=True)
            join_rate_limiter.record_attempt(client_ip, success=True)
            return JoinTeamResponse(
                status="ALREADY_MEMBER",
                team_id=team_id,
                team_name=matched_team.name,
                role=team_members[user_id].role,
                message=f"You are already an active member of team '{matched_team.name}'.",
            )

        # Check if administrative approval is required
        if matched_team.require_join_approval:
            # Check for existing pending request
            existing_req = next(
                (r for r in self._membership_requests.values()
                 if r.team_id == team_id and r.user_id == user_id and r.status == MembershipRequestStatus.PENDING),
                None,
            )
            if existing_req:
                return JoinTeamResponse(
                    status="PENDING_APPROVAL",
                    team_id=team_id,
                    team_name=matched_team.name,
                    role=existing_req.requested_role,
                    request_id=existing_req.id,
                    message=f"Your join request for '{matched_team.name}' is already pending approval from team admins.",
                )

            req_id = f"req_{uuid.uuid4().hex[:12]}"
            effective_role = requested_role or matched_team.default_join_role
            request_obj = MembershipRequest(
                id=req_id,
                team_id=team_id,
                project_id=matched_team.project_id,
                user_id=user_id,
                user_email=user_email,
                user_name=user_name,
                requested_role=effective_role,
                status=MembershipRequestStatus.PENDING,
                created_at=now.isoformat(),
            )
            self._membership_requests[req_id] = request_obj

            self._record_audit_event(
                team_id=team_id,
                actor_user_id=user_id,
                event_type=TeamAuditEventType.MEMBERSHIP_REQUEST_CREATED,
                target_user_id=user_id,
                request_id=request_id,
                metadata={"requested_role": effective_role.value},
            )

            join_rate_limiter.record_attempt(user_id, success=True)
            join_rate_limiter.record_attempt(client_ip, success=True)

            return JoinTeamResponse(
                status="PENDING_APPROVAL",
                team_id=team_id,
                team_name=matched_team.name,
                role=effective_role,
                request_id=req_id,
                message=f"Membership request submitted for '{matched_team.name}'. An admin must approve your request before access is granted.",
            )

        # Direct Join
        effective_role = requested_role or matched_team.default_join_role
        new_member = TeamMember(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            team_id=team_id,
            user_id=user_id,
            email=user_email,
            name=user_name,
            role=effective_role,
            status=TeamMemberStatus.ACTIVE,
            joined_at=now.isoformat(),
            updated_at=now.isoformat(),
        )
        team_members[user_id] = new_member
        matched_team.member_count = sum(1 for m in team_members.values() if m.status == TeamMemberStatus.ACTIVE)
        matched_team.updated_at = now.isoformat()

        join_rate_limiter.record_attempt(user_id, success=True)
        join_rate_limiter.record_attempt(client_ip, success=True)

        # Audit
        self._record_audit_event(
            team_id=team_id,
            actor_user_id=user_id,
            event_type=TeamAuditEventType.MEMBER_JOINED,
            target_user_id=user_id,
            request_id=request_id,
            metadata={"team_name": matched_team.name, "role": effective_role.value},
        )

        return JoinTeamResponse(
            status="JOINED",
            team_id=team_id,
            team_name=matched_team.name,
            role=effective_role,
            message=f"Successfully joined team '{matched_team.name}'.",
        )

    # -----------------------------------------------------------------------
    # Membership Requests Approval Workflow
    # -----------------------------------------------------------------------

    def list_membership_requests(self, team_id: str, actor_user_id: str) -> List[MembershipRequest]:
        """Lists pending membership requests for a team. Allowed for OWNER and ADMIN."""
        self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]
        if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can view membership requests.")

        return [
            r for r in self._membership_requests.values()
            if r.team_id == team_id and r.status == MembershipRequestStatus.PENDING
        ]

    def review_membership_request(
        self,
        request_id: str,
        action: str,  # "APPROVE" or "REJECT"
        actor_user_id: str,
        assigned_role: Optional[TeamRole] = None,
        reason: Optional[str] = None,
        request_id_header: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Approves or rejects a pending membership request."""
        req = self._membership_requests.get(request_id)
        if not req or req.status != MembershipRequestStatus.PENDING:
            raise ValueError("Membership request not found or already processed.")

        team = self.get_team(req.team_id, actor_user_id)
        actor = self._members[req.team_id][actor_user_id]
        if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can review membership requests.")

        now = datetime.now(timezone.utc).isoformat()
        act_upper = action.strip().upper()

        if act_upper == "APPROVE":
            req.status = MembershipRequestStatus.APPROVED
            req.reviewed_by = actor_user_id
            req.reviewed_at = now

            final_role = assigned_role or req.requested_role
            team_members = self._members.setdefault(req.team_id, {})
            new_member = TeamMember(
                id=f"mem_{uuid.uuid4().hex[:12]}",
                team_id=req.team_id,
                user_id=req.user_id,
                email=req.user_email,
                name=req.user_name,
                role=final_role,
                status=TeamMemberStatus.ACTIVE,
                joined_at=now,
                updated_at=now,
            )
            team_members[req.user_id] = new_member
            team.member_count = sum(1 for m in team_members.values() if m.status == TeamMemberStatus.ACTIVE)
            team.updated_at = now

            self._record_audit_event(
                team_id=req.team_id,
                actor_user_id=actor_user_id,
                event_type=TeamAuditEventType.MEMBERSHIP_REQUEST_APPROVED,
                target_user_id=req.user_id,
                request_id=request_id_header,
                metadata={"role": final_role.value},
            )
            self._record_audit_event(
                team_id=req.team_id,
                actor_user_id=req.user_id,
                event_type=TeamAuditEventType.MEMBER_JOINED,
                target_user_id=req.user_id,
                request_id=request_id_header,
                metadata={"team_name": team.name, "role": final_role.value},
            )
            return {"status": "APPROVED", "user_id": req.user_id, "role": final_role.value}

        elif act_upper == "REJECT":
            req.status = MembershipRequestStatus.REJECTED
            req.reviewed_by = actor_user_id
            req.reviewed_at = now
            req.rejection_reason = reason or "Request declined by administrator."

            self._record_audit_event(
                team_id=req.team_id,
                actor_user_id=actor_user_id,
                event_type=TeamAuditEventType.MEMBERSHIP_REQUEST_REJECTED,
                target_user_id=req.user_id,
                request_id=request_id_header,
                metadata={"reason": req.rejection_reason},
            )
            return {"status": "REJECTED", "user_id": req.user_id, "reason": req.rejection_reason}
        else:
            raise ValueError("Action must be either APPROVE or REJECT.")

    # -----------------------------------------------------------------------
    # Code Rotation & Revocation
    # -----------------------------------------------------------------------

    def rotate_join_code(
        self,
        team_id: str,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> RotateJoinCodeResponse:
        """Rotates the WL-XXXXXX join code. Allowed for OWNER and ADMIN only."""
        team = self.get_team(team_id, actor_user_id)
        member = self._members[team_id][actor_user_id]

        if member.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can rotate the join code.")

        plaintext_code, new_digest = self._generate_unique_join_code()
        now = datetime.now(timezone.utc)
        ttl = self._get_ttl_seconds()
        expires_at = (now + timedelta(seconds=ttl)).isoformat()

        team.join_code_digest = new_digest
        team.join_code_created_at = now.isoformat()
        team.join_code_expires_at = expires_at
        team.join_code_enabled = True
        team.updated_at = now.isoformat()

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.JOIN_CODE_ROTATED,
            request_id=request_id,
            metadata={"expires_at": expires_at},
        )

        return RotateJoinCodeResponse(
            team_id=team_id,
            join_code=plaintext_code,
            expires_at=expires_at,
        )

    def revoke_join_code(
        self,
        team_id: str,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> RevokeJoinCodeResponse:
        """Disables the current join code immediately."""
        team = self.get_team(team_id, actor_user_id)
        member = self._members[team_id][actor_user_id]

        if member.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can revoke the join code.")

        team.join_code_enabled = False
        team.updated_at = datetime.now(timezone.utc).isoformat()

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.JOIN_CODE_REVOKED,
            request_id=request_id,
        )

        return RevokeJoinCodeResponse(team_id=team_id)

    # -----------------------------------------------------------------------
    def add_member(
        self,
        team_id: str,
        actor_user_id: str,
        target_user_id: str,
        role: TeamRole = TeamRole.ENGINEER,
        target_name: Optional[str] = None,
        target_email: Optional[str] = None,
    ) -> TeamMember:
        """Directly adds an active member to the team (requires OWNER or ADMIN)."""
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id].get(actor_user_id)
        if not actor or actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can add members.")

        now = datetime.now(timezone.utc).isoformat()
        team_members = self._members.setdefault(team_id, {})
        new_member = TeamMember(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            team_id=team_id,
            user_id=target_user_id,
            email=target_email,
            name=target_name or target_user_id,
            role=role,
            status=TeamMemberStatus.ACTIVE,
            joined_at=now,
            updated_at=now,
        )
        team_members[target_user_id] = new_member
        team.member_count = sum(1 for m in team_members.values() if m.status == TeamMemberStatus.ACTIVE)
        team.updated_at = now
        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.MEMBER_JOINED,
            target_user_id=target_user_id,
            metadata={"role": role.value if hasattr(role, "value") else str(role)},
        )
        return new_member

    def get_member(self, team_id: str, user_id: str) -> Optional[TeamMember]:
        """Returns active member if user belongs to the team."""
        members = self._members.get(team_id, {})
        mem = members.get(user_id)
        if mem and mem.status == TeamMemberStatus.ACTIVE:
            return mem
        return None

    def list_members(self, team_id: str, actor_user_id: str) -> List[Dict[str, Any]]:
        """Lists active team members."""
        self.get_team(team_id, actor_user_id)
        return [
            {
                "id": m.id,
                "team_id": m.team_id,
                "user_id": m.user_id,
                "email": m.email,
                "name": m.name,
                "role": m.role.value if hasattr(m.role, "value") else str(m.role),
                "status": m.status.value if hasattr(m.status, "value") else str(m.status),
                "joined_at": m.joined_at,
            }
            for m in self._members.get(team_id, {}).values()
            if m.status == TeamMemberStatus.ACTIVE
        ]

    def update_member_role(
        self,
        team_id: str,
        target_user_id: str,
        new_role: TeamRole,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Updates member role with owner protection."""
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]
        members = self._members[team_id]

        if target_user_id not in members or members[target_user_id].status != TeamMemberStatus.ACTIVE:
            raise ValueError("Target user is not an active member of this team.")

        target = members[target_user_id]

        if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only OWNER or ADMIN can change member roles.")

        # ADMIN cannot change role of OWNER or grant OWNER role
        if actor.role == TeamRole.ADMIN:
            if target.role == TeamRole.OWNER or new_role == TeamRole.OWNER:
                raise PermissionDeniedError("ADMIN cannot modify OWNER permissions.")

        # OWNER protection: Cannot demote sole owner
        if target.role == TeamRole.OWNER and new_role != TeamRole.OWNER:
            owners = [m for m in members.values() if m.role == TeamRole.OWNER and m.status == TeamMemberStatus.ACTIVE]
            if len(owners) <= 1:
                raise PermissionDeniedError("Cannot demote the sole team OWNER. Transfer ownership first.")

        old_role = target.role
        target.role = new_role
        target.updated_at = datetime.now(timezone.utc).isoformat()

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.MEMBER_ROLE_CHANGED,
            target_user_id=target_user_id,
            request_id=request_id,
            metadata={"old_role": old_role.value if hasattr(old_role, "value") else str(old_role),
                      "new_role": new_role.value if hasattr(new_role, "value") else str(new_role)},
        )

        return {"status": "SUCCESS", "user_id": target_user_id, "new_role": new_role.value}

    def remove_member(
        self,
        team_id: str,
        target_user_id: str,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Removes a member from the team. Prevents removing the sole OWNER."""
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]
        members = self._members[team_id]

        if target_user_id not in members or members[target_user_id].status != TeamMemberStatus.ACTIVE:
            raise ValueError("Target user is not an active member of this team.")

        target = members[target_user_id]

        # Self-leave vs Removal by Admin/Owner
        if actor_user_id != target_user_id:
            if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
                raise PermissionDeniedError("Only OWNER or ADMIN can remove team members.")
            if actor.role == TeamRole.ADMIN and target.role in (TeamRole.OWNER, TeamRole.ADMIN):
                raise PermissionDeniedError("ADMIN cannot remove OWNER or fellow ADMIN.")

        # Cannot remove sole OWNER
        if target.role == TeamRole.OWNER:
            owners = [m for m in members.values() if m.role == TeamRole.OWNER and m.status == TeamMemberStatus.ACTIVE]
            if len(owners) <= 1:
                raise PermissionDeniedError("Cannot remove the team OWNER.")

        target.status = TeamMemberStatus.REMOVED
        target.updated_at = datetime.now(timezone.utc).isoformat()
        team.member_count = sum(1 for m in members.values() if m.status == TeamMemberStatus.ACTIVE)
        team.updated_at = datetime.now(timezone.utc).isoformat()

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.MEMBER_REMOVED,
            target_user_id=target_user_id,
            request_id=request_id,
        )

        return {"status": "REMOVED", "user_id": target_user_id}

    # -----------------------------------------------------------------------
    # Ownership Transfer
    # -----------------------------------------------------------------------

    def transfer_ownership(
        self,
        team_id: str,
        target_user_id: str,
        actor_user_id: str,
        confirmation_phrase: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Transfers team ownership to another active team member with explicit confirmation.
        Only the current OWNER can initiate ownership transfer.
        """
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]

        if actor.role != TeamRole.OWNER:
            raise PermissionDeniedError("Only the current team OWNER can transfer ownership.")

        if actor_user_id == target_user_id:
            raise ValueError("You are already the owner of this team.")

        members = self._members[team_id]
        if target_user_id not in members or members[target_user_id].status != TeamMemberStatus.ACTIVE:
            raise ValueError("Target user must be an active member of the team to receive ownership.")

        # Check confirmation phrase (team name)
        if confirmation_phrase.strip().lower() != team.name.strip().lower():
            raise ValueError(f"Confirmation phrase must exactly match the team name: '{team.name}'.")

        target = members[target_user_id]
        now = datetime.now(timezone.utc).isoformat()

        # Reassign roles
        target.role = TeamRole.OWNER
        target.updated_at = now
        actor.role = TeamRole.ADMIN
        actor.updated_at = now

        team.owner_id = target_user_id
        team.updated_at = now

        self._record_audit_event(
            team_id=team_id,
            actor_user_id=actor_user_id,
            event_type=TeamAuditEventType.OWNERSHIP_TRANSFERRED,
            target_user_id=target_user_id,
            request_id=request_id,
            metadata={"previous_owner": actor_user_id, "new_owner": target_user_id},
        )

        return {
            "status": "TRANSFERRED",
            "previous_owner": actor_user_id,
            "new_owner": target_user_id,
            "team_id": team_id,
        }

    # -----------------------------------------------------------------------
    # Project ↔ Team Authorization
    # -----------------------------------------------------------------------

    def associate_project(self, project_id: str, team_id: str, actor_user_id: str) -> None:
        """Associates a project with a team."""
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]
        if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can link projects to the team.")
        self._project_teams[project_id] = team_id
        team.project_id = project_id

    def verify_project_access(
        self,
        project_id: str,
        user_id: str,
        required_role: Optional[TeamRole] = None,
    ) -> bool:
        """Verifies if user has permission to access a project via team membership."""
        team_id = self._project_teams.get(project_id)
        if not team_id:
            return True

        members = self._members.get(team_id, {})
        if user_id not in members or members[user_id].status != TeamMemberStatus.ACTIVE:
            return False

        if required_role:
            member_role = members[user_id].role
            role_hierarchy = {
                TeamRole.VIEWER: 1,
                TeamRole.MEMBER: 2,
                TeamRole.RESEARCHER: 2,
                TeamRole.ENGINEER: 3,
                TeamRole.ADMIN: 4,
                TeamRole.OWNER: 5,
            }
            return role_hierarchy.get(member_role, 0) >= role_hierarchy.get(required_role, 0)

        return True

    def get_audit_logs(self, team_id: str, actor_user_id: str) -> List[Dict[str, Any]]:
        """Retrieves audit trail for a team."""
        self.get_team(team_id, actor_user_id)
        return [
            {
                "event_id": log.event_id,
                "team_id": log.team_id,
                "actor_user_id": log.actor_user_id,
                "target_user_id": log.target_user_id,
                "event_type": log.event_type.value if hasattr(log.event_type, "value") else str(log.event_type),
                "timestamp": log.timestamp,
                "metadata": log.metadata,
            }
            for log in self._audit_logs
            if log.team_id == team_id
        ]


# Global singleton instance
team_service = TeamService()
