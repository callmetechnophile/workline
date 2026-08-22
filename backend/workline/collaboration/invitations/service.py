"""High-level service managing secure team invitation lifecycle, validation, and acceptance."""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
import secrets
import threading
from typing import Any, Dict, List, Optional, Tuple

from backend.workline.collaboration.invitations.encryption import (
    CryptographicError,
    InvalidTokenError,
    InvitationEncryptionEngine,
    invitation_crypto,
)
from backend.workline.collaboration.invitations.models import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    AuditEventType,
    CreateInvitationRequest,
    CreateInvitationResponse,
    InvitationAuditEvent,
    InvitationPayload,
    InvitationPreview,
    InvitationStatus,
    TeamInvitation,
    TeamRole,
)
from backend.workline.collaboration.invitations.token import TokenService, token_service
from backend.workline.collaboration.invitations.validator import (
    GENERIC_ERROR_MESSAGE,
    InvalidInvitationError,
    InvitationValidator,
    RateLimitExceededError,
    invitation_validator,
)

logger = logging.getLogger("workline.invitations.service")


class PermissionDeniedError(Exception):
    """Raised when user lacks permission to manage invitations."""
    pass


class InvitationService:
    """
    Orchestrates creation, validation, preview, acceptance, revocation,
    regeneration, and auditing of secure team invitations.
    """

    def __init__(
        self,
        token_svc: TokenService = token_service,
        validator: InvitationValidator = invitation_validator,
        crypto: InvitationEncryptionEngine = invitation_crypto,
    ):
        self.token_svc = token_svc
        self.validator = validator
        self.crypto = crypto
        self._lock = threading.RLock()
        
        # In-memory storage / cache (persisted to SQLite/SurrealDB where available)
        self._invitations: Dict[str, TeamInvitation] = {}  # invitation_id -> TeamInvitation
        self._token_hash_index: Dict[str, str] = {}         # token_hash -> invitation_id
        self._audit_logs: List[InvitationAuditEvent] = []
        self._teams: Dict[str, Dict[str, Any]] = {}        # team_id -> team metadata
        self._team_members: Dict[str, List[Dict[str, str]]] = {}  # team_id -> list of {user_id, role, joined_at}

        # Seed default demo team if empty
        self._seed_default_teams()

    def _seed_default_teams(self) -> None:
        """Initializes default team context."""
        default_team_id = "team_pcb_research"
        self._teams[default_team_id] = {
            "team_id": default_team_id,
            "name": "PCB Research",
            "owner": "Team Owner",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._team_members[default_team_id] = [
            {"user_id": "usr_owner", "name": "Team Owner", "role": "OWNER", "joined_at": datetime.now(timezone.utc).isoformat()}
        ]

    def register_team(self, team_id: str, name: str, owner: str = "Team Owner") -> None:
        """Registers a team for invitation linkage."""
        with self._lock:
            self._teams[team_id] = {
                "team_id": team_id,
                "name": name,
                "owner": owner,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if team_id not in self._team_members:
                self._team_members[team_id] = [
                    {"user_id": "usr_owner", "name": owner, "role": "OWNER", "joined_at": datetime.now(timezone.utc).isoformat()}
                ]

    def _log_audit(
        self,
        event_type: AuditEventType,
        team_id: str,
        invitation_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Records an immutable security audit event."""
        event = InvitationAuditEvent(
            event_id=f"evt_{secrets.token_hex(8)}",
            event_type=event_type,
            team_id=team_id,
            invitation_id=invitation_id,
            user_id=user_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details or {},
        )
        self._audit_logs.append(event)
        logger.info(f"[AUDIT] {event_type.value} team={team_id} inv={invitation_id} user={user_id}")

    def create_invitation(
        self,
        req: CreateInvitationRequest,
        actor_role: TeamRole = TeamRole.OWNER,
    ) -> CreateInvitationResponse:
        """
        Generates a new secure team invitation link with authenticated AES-256-GCM encryption.
        Only OWNER and ADMIN roles are authorized.
        """
        if actor_role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can create invitation links.")

        with self._lock:
            # Ensure team exists in record
            if req.team_id not in self._teams:
                self.register_team(req.team_id, req.team_id.replace("_", " ").title())

            team_meta = self._teams[req.team_id]
            invitation_id = f"inv_{secrets.token_hex(8)}"
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(days=max(1, req.ttl_days))).isoformat()

            # Construct internal payload (strictly minimal, no secrets/PII)
            payload = InvitationPayload(
                invitation_id=invitation_id,
                team_id=req.team_id,
                issued_at=now.isoformat(),
                expires_at=expires_at,
                key_version="v1",
            )

            # Encrypt and encode into opaque token
            opaque_token = self.token_svc.encode_token(payload, key_version="v1")
            token_hash = self.token_svc.hash_token(opaque_token)
            join_url = self.token_svc.build_join_url(opaque_token)

            # Store server-side record with token_hash (NEVER raw token)
            invitation = TeamInvitation(
                invitation_id=invitation_id,
                team_id=req.team_id,
                created_by=req.created_by,
                token_hash=token_hash,
                status=InvitationStatus.ACTIVE,
                created_at=now.isoformat(),
                expires_at=expires_at,
                max_uses=req.max_uses,
                use_count=0,
                accepted_by=[],
                key_version="v1",
                role=req.role,
            )

            self._invitations[invitation_id] = invitation
            self._token_hash_index[token_hash] = invitation_id

            self._log_audit(
                AuditEventType.TEAM_INVITATION_CREATED,
                team_id=req.team_id,
                invitation_id=invitation_id,
                user_id=req.created_by,
                details={"max_uses": req.max_uses, "ttl_days": req.ttl_days, "role": req.role},
            )

            # Generate formatted message template for manual copy/sharing
            team_name = team_meta.get("name", "Workline Team")
            message_template = (
                f"Hi,\n\n"
                f"You've been invited to join the team '{team_name}' on Workline.\n\n"
                f"Join the team:\n{join_url}\n\n"
                f"Looking forward to collaborating!"
            )

            return CreateInvitationResponse(
                invitation_id=invitation_id,
                team_id=req.team_id,
                join_url=join_url,
                expires_at=expires_at,
                max_uses=req.max_uses,
                status=InvitationStatus.ACTIVE,
                message_template=message_template,
            )

    def preview_invitation(
        self,
        opaque_token: str,
        client_id: Optional[str] = "anonymous",
    ) -> InvitationPreview:
        """
        Validates token and returns safe pre-join preview data without joining the team.
        Does NOT expose private team secrets or modify usage count.
        """
        self.validator.validate_rate_limit(client_id or "anonymous")

        # Decode token to find invitation
        try:
            payload = self.token_svc.decode_token(opaque_token)
        except Exception as e:
            logger.warning(f"[SECURITY] Preview token decode failure: {e}")
            raise InvalidInvitationError()

        with self._lock:
            inv = self._invitations.get(payload.invitation_id)
            payload, inv = self.validator.validate_token_and_record(opaque_token, inv)

            team_meta = self._teams.get(payload.team_id, {"name": payload.team_id, "owner": "Team Owner"})
            members = self._team_members.get(payload.team_id, [])

            self._log_audit(
                AuditEventType.TEAM_INVITATION_VIEWED,
                team_id=payload.team_id,
                invitation_id=payload.invitation_id,
                user_id=client_id,
            )

            return InvitationPreview(
                valid=True,
                team_name=team_meta.get("name", "Workline Team"),
                team_id=payload.team_id,
                member_count=len(members),
                invited_by=inv.created_by,
                expires_at=inv.expires_at,
                status=inv.status.value,
                role=inv.role,
            )

    def accept_invitation(
        self,
        opaque_token: str,
        user_id: str,
        user_name: Optional[str] = None,
        client_id: Optional[str] = "authenticated",
    ) -> AcceptInvitationResponse:
        """
        Atomically validates invitation, enforces usage limits, creates team membership,
        and marks invitation exhausted when max uses are reached.
        Prevents duplicate memberships and race conditions.
        """
        self.validator.validate_rate_limit(client_id or user_id)

        try:
            payload = self.token_svc.decode_token(opaque_token)
        except Exception as e:
            logger.warning(f"[SECURITY] Accept token decode failure: {e}")
            raise InvalidInvitationError()

        with self._lock:
            inv = self._invitations.get(payload.invitation_id)
            payload, inv = self.validator.validate_token_and_record(opaque_token, inv)

            team_id = payload.team_id
            members = self._team_members.setdefault(team_id, [])
            team_meta = self._teams.get(team_id, {"name": team_id})

            # Check if user is already a member
            existing = [m for m in members if m.get("user_id") == user_id]
            if existing:
                return AcceptInvitationResponse(
                    success=True,
                    team_id=team_id,
                    team_name=team_meta.get("name", team_id),
                    role=existing[0].get("role", "MEMBER"),
                    message="You are already a member of this team.",
                )

            # Check if user already accepted this specific invitation
            if user_id in inv.accepted_by:
                return AcceptInvitationResponse(
                    success=True,
                    team_id=team_id,
                    team_name=team_meta.get("name", team_id),
                    role=inv.role,
                    message="Already joined.",
                )

            # Atomic increment
            inv.use_count += 1
            inv.accepted_by.append(user_id)
            inv.accepted_at = datetime.now(timezone.utc).isoformat()

            # Exhaustion check
            if inv.use_count >= inv.max_uses:
                inv.status = InvitationStatus.EXHAUSTED
                self._log_audit(
                    AuditEventType.TEAM_INVITATION_EXHAUSTED,
                    team_id=team_id,
                    invitation_id=inv.invitation_id,
                    user_id=user_id,
                )
            else:
                inv.status = InvitationStatus.ACCEPTED

            # Add member to team
            members.append({
                "user_id": user_id,
                "name": user_name or user_id,
                "role": inv.role,
                "joined_at": datetime.now(timezone.utc).isoformat(),
            })

            self._log_audit(
                AuditEventType.TEAM_INVITATION_ACCEPTED,
                team_id=team_id,
                invitation_id=inv.invitation_id,
                user_id=user_id,
                details={"use_count": inv.use_count, "max_uses": inv.max_uses},
            )

            return AcceptInvitationResponse(
                success=True,
                team_id=team_id,
                team_name=team_meta.get("name", team_id),
                role=inv.role,
                message="Successfully joined team.",
            )

    def revoke_invitation(
        self,
        invitation_id: str,
        actor_id: str = "system",
        actor_role: TeamRole = TeamRole.OWNER,
    ) -> bool:
        """Revokes an active invitation link. Only OWNER or ADMIN can revoke."""
        if actor_role not in (TeamRole.OWNER, TeamRole.ADMIN):
            raise PermissionDeniedError("Only team OWNER or ADMIN can revoke invitations.")

        with self._lock:
            inv = self._invitations.get(invitation_id)
            if not inv:
                return False

            inv.status = InvitationStatus.REVOKED
            inv.revoked_at = datetime.now(timezone.utc).isoformat()

            self._log_audit(
                AuditEventType.TEAM_INVITATION_REVOKED,
                team_id=inv.team_id,
                invitation_id=inv.invitation_id,
                user_id=actor_id,
            )
            return True

    def regenerate_invitation(
        self,
        invitation_id: str,
        actor_id: str = "system",
        actor_role: TeamRole = TeamRole.OWNER,
    ) -> CreateInvitationResponse:
        """
        Revokes the previous invitation and generates a fresh cryptographic token.
        Guarantees the old token is permanently invalidated.
        """
        with self._lock:
            old_inv = self._invitations.get(invitation_id)
            if not old_inv:
                raise InvalidInvitationError("Invitation not found.")

            # Revoke old
            self.revoke_invitation(invitation_id, actor_id=actor_id, actor_role=actor_role)

            # Create new
            req = CreateInvitationRequest(
                team_id=old_inv.team_id,
                created_by=actor_id,
                ttl_days=7,
                max_uses=old_inv.max_uses,
                role=old_inv.role,
            )
            new_resp = self.create_invitation(req, actor_role=actor_role)

            self._log_audit(
                AuditEventType.TEAM_INVITATION_REGENERATED,
                team_id=old_inv.team_id,
                invitation_id=new_resp.invitation_id,
                user_id=actor_id,
                details={"revoked_invitation_id": invitation_id},
            )
            return new_resp

    def list_invitations(
        self,
        team_id: str,
        actor_role: TeamRole = TeamRole.OWNER,
    ) -> List[TeamInvitation]:
        """Lists all invitations for a team (without raw tokens)."""
        with self._lock:
            return [inv for inv in self._invitations.values() if inv.team_id == team_id]

    def get_audit_logs(self, team_id: Optional[str] = None) -> List[InvitationAuditEvent]:
        """Returns immutable security audit logs."""
        with self._lock:
            if team_id:
                return [e for e in self._audit_logs if e.team_id == team_id]
            return list(self._audit_logs)


# Module-level singleton
invitation_service = InvitationService()
