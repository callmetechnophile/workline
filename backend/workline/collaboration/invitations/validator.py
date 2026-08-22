"""Security validator, rate limiter, and integrity verifier for team invitations."""

from collections import defaultdict
from datetime import datetime, timezone
import logging
import time
from typing import Dict, List, Optional, Tuple

from backend.workline.collaboration.invitations.encryption import (
    CryptographicError,
    InvalidTokenError,
)
from backend.workline.collaboration.invitations.models import (
    InvitationPayload,
    InvitationStatus,
    TeamInvitation,
)
from backend.workline.collaboration.invitations.token import TokenService, token_service

logger = logging.getLogger("workline.invitations.validator")

GENERIC_ERROR_MESSAGE = "This invitation is invalid or no longer available."


class InvalidInvitationError(Exception):
    """
    Raised when an invitation fails security, expiration, or status checks.
    Always uses generic message for external callers to prevent information leakage.
    """

    def __init__(self, message: str = GENERIC_ERROR_MESSAGE, internal_reason: Optional[str] = None):
        super().__init__(message)
        self.internal_reason = internal_reason or message


class RateLimitExceededError(Exception):
    """Raised when rate limits are exceeded."""

    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message)


class InvitationRateLimiter:
    """
    Sliding window rate limiter to protect token preview and accept endpoints
    against enumeration and brute-force guessing attacks.
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._history: Dict[str, List[float]] = defaultdict(list)

    def check_rate_limit(self, identifier: str) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        now = time.time()
        cutoff = now - self.window_seconds
        window = [t for t in self._history[identifier] if t > cutoff]
        if len(window) >= self.max_requests:
            return False
        window.append(now)
        self._history[identifier] = window
        return True

    def reset(self) -> None:
        """Clears all rate limit history."""
        self._history.clear()


class InvitationValidator:
    """
    Executes deep validation of invitation tokens, database states, expiration,
    and usage constraints while enforcing strict information-leakage prevention.
    """

    def __init__(self, token_svc: TokenService = token_service):
        self.token_svc = token_svc
        self.rate_limiter = InvitationRateLimiter(max_requests=60, window_seconds=60)

    def validate_rate_limit(self, client_id: str) -> None:
        """Enforces rate limit for token inspection/preview."""
        if not self.rate_limiter.check_rate_limit(client_id):
            logger.warning(f"[SECURITY] Rate limit exceeded for client '{client_id}'.")
            raise RateLimitExceededError()

    def validate_token_and_record(
        self,
        opaque_token: str,
        invitation_record: Optional[TeamInvitation],
    ) -> Tuple[InvitationPayload, TeamInvitation]:
        """
        Validates token payload integrity, cryptographic authentication tag,
        expiration, revocation status, and usage thresholds.
        """
        # 1. Decrypt and verify cryptographic tag
        try:
            payload = self.token_svc.decode_token(opaque_token)
        except (CryptographicError, InvalidTokenError, Exception) as e:
            logger.warning(f"[SECURITY] Invitation decryption failed: {e}")
            raise InvalidInvitationError(internal_reason=f"Decryption failed: {e}")

        # 2. Check existence of database record
        if not invitation_record:
            logger.warning(f"[SECURITY] No database record for invitation_id '{payload.invitation_id}'.")
            raise InvalidInvitationError(internal_reason="Invitation not found in database.")

        # 3. Check token hash fingerprint matches
        expected_hash = self.token_svc.hash_token(opaque_token)
        if invitation_record.token_hash != expected_hash:
            logger.warning(f"[SECURITY] Token hash mismatch for invitation_id '{payload.invitation_id}'.")
            raise InvalidInvitationError(internal_reason="Token hash mismatch.")

        # 4. Check revocation status
        if invitation_record.status == InvitationStatus.REVOKED:
            logger.info(f"[SECURITY] Attempted access to revoked invitation '{payload.invitation_id}'.")
            raise InvalidInvitationError(internal_reason="Invitation was revoked.")

        # 5. Check expiration timestamp
        now_iso = datetime.now(timezone.utc).isoformat()
        if now_iso > payload.expires_at or now_iso > invitation_record.expires_at:
            logger.info(f"[SECURITY] Invitation '{payload.invitation_id}' has expired.")
            raise InvalidInvitationError(internal_reason="Invitation expired.")

        # 6. Check usage count / exhaustion
        if invitation_record.status == InvitationStatus.EXHAUSTED or invitation_record.use_count >= invitation_record.max_uses:
            logger.info(f"[SECURITY] Invitation '{payload.invitation_id}' is exhausted ({invitation_record.use_count}/{invitation_record.max_uses}).")
            raise InvalidInvitationError(internal_reason="Invitation exhausted.")

        return payload, invitation_record


# Module-level singleton
invitation_validator = InvitationValidator()
