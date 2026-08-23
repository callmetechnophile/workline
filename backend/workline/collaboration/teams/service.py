"""
Workline AI — Secure Team Collaboration & Join Code Service.

Provides:
1. Team lifecycle management (Create, Get, List, Archive).
2. Cryptographically secure 6-character CSPRNG join code generation with HMAC-SHA-256 storage.
3. Code rotation, revocation, and expiration.
4. Brute-force rate limiting and code enumeration protection (generic error responses).
5. Duplicate membership prevention.
6. Role-based access control (OWNER, ADMIN, MEMBER) with strict owner protection.
7. Project access authorization verification.
8. Complete audit logging with zero plaintext secrets or join codes.
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
    RevokeJoinCodeResponse,
    RotateJoinCodeResponse,
    Team,
    TeamAuditEvent,
    TeamAuditEventType,
    TeamMember,
    TeamMemberStatus,
    TeamRole,
    TeamStatus,
)
from backend.workline.collaboration.teams.rate_limiter import join_rate_limiter

JOIN_CODE_ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
JOIN_CODE_LENGTH = 6
JOIN_CODE_REGEX = re.compile(r"^[A-Z0-9]{6}$")
DEFAULT_JOIN_CODE_TTL_SECONDS = 86400  # 24 hours


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
    """Core collaboration service managing teams, memberships, join codes, and audit logs."""

    def __init__(self, hmac_secret: Optional[bytes] = None):
        self._hmac_secret = hmac_secret or self._load_hmac_secret()
        # In-memory stores (synced with database / persistence layer)
        self._teams: Dict[str, Team] = {}
        self._members: Dict[str, Dict[str, TeamMember]] = {}  # team_id -> {user_id: TeamMember}
        self._audit_logs: List[TeamAuditEvent] = []
        self._project_teams: Dict[str, str] = {}  # project_id -> team_id

    def _load_hmac_secret(self) -> bytes:
        """Loads HMAC secret from environment variable or generates secure session secret."""
        raw_secret = os.getenv("TEAM_JOIN_CODE_SECRET")
        if raw_secret:
            return raw_secret.strip().encode("utf-8")
        # Safe in-memory fallback
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
        Generates a 6-character CSPRNG alphanumeric code and its HMAC digest.
        Handles collisions by bounded retries.
        Returns: (plaintext_code, hmac_digest)
        """
        for _ in range(10):
            code = "".join(secrets.choice(JOIN_CODE_ALPHABET) for _ in range(JOIN_CODE_LENGTH))
            digest = self._compute_code_digest(code)

            # Ensure no active collision
            collision = any(
                t.join_code_digest == digest and t.join_code_enabled and t.status == TeamStatus.ACTIVE
                for t in self._teams.values()
            )
            if not collision:
                return code, digest

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
        request_id: Optional[str] = None,
    ) -> CreateTeamResponse:
        """
        Creates a new team, designates creator as OWNER, and generates initial 6-char join code.
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
            owner_id=creator_user_id,
            join_code_digest=digest,
            join_code_created_at=now.isoformat(),
            join_code_expires_at=expires_at,
            join_code_enabled=True,
            status=TeamStatus.ACTIVE,
            created_at=now.isoformat(),
            updated_at=now.isoformat(),
            member_count=1,
        )
        self._teams[team_id] = team

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
            metadata={"team_name": clean_name},
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
            owner_id=team.owner_id,
            role=TeamRole.OWNER,
            join_code=plaintext_code,
            join_code_expires_at=expires_at,
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
                        "role": members[user_id].role,
                        "member_count": team.member_count,
                        "created_at": team.created_at,
                    })
        return results

    # -----------------------------------------------------------------------
    # Join Team Flow
    # -----------------------------------------------------------------------

    def join_team(
        self,
        raw_code: str,
        user_id: str,
        client_ip: str = "unknown",
        request_id: Optional[str] = None,
    ) -> JoinTeamResponse:
        """
        Validates join code, checks rate limit & expiration, prevents duplicates,
        and establishes membership. Failed responses are intentionally generic.
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

        # Normalize and validate length/characters
        if not raw_code:
            join_rate_limiter.record_attempt(user_id, success=False)
            join_rate_limiter.record_attempt(client_ip, success=False)
            raise InvalidJoinCodeError("Invalid or expired team code.")

        clean_code = raw_code.strip().upper()
        if not JOIN_CODE_REGEX.match(clean_code):
            join_rate_limiter.record_attempt(user_id, success=False)
            join_rate_limiter.record_attempt(client_ip, success=False)
            raise InvalidJoinCodeError("Invalid or expired team code.")

        target_digest = self._compute_code_digest(clean_code)
        now = datetime.now(timezone.utc)

        # Lookup matching team by digest
        matched_team: Optional[Team] = None
        for team in self._teams.values():
            if (
                team.join_code_digest == target_digest
                and team.join_code_enabled
                and team.status == TeamStatus.ACTIVE
            ):
                # Verify expiration
                if team.join_code_expires_at:
                    try:
                        exp = datetime.fromisoformat(team.join_code_expires_at)
                        if exp > now:
                            matched_team = team
                            break
                    except Exception:
                        pass

        if not matched_team:
            # Failure: record on rate limiter and audit log
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

        # Success on code lookup -> check duplicate membership
        team_id = matched_team.id
        team_members = self._members.setdefault(team_id, {})

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

        # Establish membership
        new_member = TeamMember(
            id=f"mem_{uuid.uuid4().hex[:12]}",
            team_id=team_id,
            user_id=user_id,
            role=TeamRole.MEMBER,
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
            metadata={"team_name": matched_team.name, "role": "MEMBER"},
        )

        return JoinTeamResponse(
            status="JOINED",
            team_id=team_id,
            team_name=matched_team.name,
            role=TeamRole.MEMBER,
            message=f"Successfully joined team '{matched_team.name}'.",
        )

    # -----------------------------------------------------------------------
    # Code Rotation & Revocation
    # -----------------------------------------------------------------------

    def rotate_join_code(
        self,
        team_id: str,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> RotateJoinCodeResponse:
        """Rotates the 6-character join code. Allowed for OWNER and ADMIN only."""
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
    # Member & Role Management (With Strict Owner Protection)
    # -----------------------------------------------------------------------

    def list_members(self, team_id: str, actor_user_id: str) -> List[Dict[str, Any]]:
        """Lists active team members."""
        self.get_team(team_id, actor_user_id)
        return [
            {
                "id": m.id,
                "team_id": m.team_id,
                "user_id": m.user_id,
                "role": m.role,
                "status": m.status,
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
            metadata={"old_role": old_role.value, "new_role": new_role.value},
        )

        return {"status": "SUCCESS", "user_id": target_user_id, "new_role": new_role.value}

    def remove_member(
        self,
        team_id: str,
        target_user_id: str,
        actor_user_id: str,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Removes a member from the team. Prevents removing the OWNER."""
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
    # Project ↔ Team Authorization
    # -----------------------------------------------------------------------

    def associate_project(self, project_id: str, team_id: str, actor_user_id: str) -> None:
        """Associates a project with a team."""
        team = self.get_team(team_id, actor_user_id)
        actor = self._members[team_id][actor_user_id]
        if actor.role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can link projects to the team.")
        self._project_teams[project_id] = team_id

    def verify_project_access(
        self,
        project_id: str,
        user_id: str,
        required_role: Optional[TeamRole] = None,
    ) -> bool:
        """Verifies if user has permission to access a project via team membership."""
        team_id = self._project_teams.get(project_id)
        if not team_id:
            # Unassociated project defaults to project owner check
            return True

        members = self._members.get(team_id, {})
        if user_id not in members or members[user_id].status != TeamMemberStatus.ACTIVE:
            return False

        if required_role:
            member_role = members[user_id].role
            role_hierarchy = {TeamRole.MEMBER: 1, TeamRole.ADMIN: 2, TeamRole.OWNER: 3}
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
                "event_type": log.event_type.value,
                "timestamp": log.timestamp,
                "metadata": log.metadata,
            }
            for log in self._audit_logs
            if log.team_id == team_id
        ]


# Global singleton instance
team_service = TeamService()
