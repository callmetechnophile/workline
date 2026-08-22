"""Comprehensive end-to-end scenarios, edge cases, and audit verification for team invitations."""

from datetime import datetime, timezone
import secrets
import pytest

from backend.workline.collaboration.invitations import (
    AuditEventType,
    CreateInvitationRequest,
    GENERIC_ERROR_MESSAGE,
    InvalidInvitationError,
    InvitationService,
    InvitationStatus,
    TeamRole,
)
from backend.workline.collaboration.invitations.encryption import (
    DEFAULT_AAD,
    InvalidTokenError,
    InvitationEncryptionEngine,
)
from backend.workline.collaboration.invitations.token import TokenService
from backend.workline.project.sanitizer import SecuritySanitizer


@pytest.fixture
def service() -> InvitationService:
    svc = InvitationService()
    svc.register_team("team_avionics", "Avionics Guidance & Navigation", owner="Commander Shepard")
    svc.register_team("team_optics", "Laser Optics Unit", owner="Dr. Halsey")
    return svc


def test_multiple_teams_independent_invitations(service: InvitationService):
    """Test generating invitations across multiple separate teams without cross-talk."""
    req1 = CreateInvitationRequest(team_id="team_avionics", max_uses=2, role="ENGINEER")
    req2 = CreateInvitationRequest(team_id="team_optics", max_uses=5, role="VIEWER")

    resp1 = service.create_invitation(req1)
    resp2 = service.create_invitation(req2)

    tok1 = resp1.join_url.split("/team/join/")[1]
    tok2 = resp2.join_url.split("/team/join/")[1]

    # Previews reflect distinct teams
    prev1 = service.preview_invitation(tok1)
    prev2 = service.preview_invitation(tok2)

    assert prev1.team_name == "Avionics Guidance & Navigation"
    assert prev2.team_name == "Laser Optics Unit"
    assert prev1.role == "ENGINEER"
    assert prev2.role == "VIEWER"

    # Accepting tok1 adds to team_avionics only
    service.accept_invitation(tok1, user_id="pilot_1")
    assert any(m["user_id"] == "pilot_1" for m in service._team_members["team_avionics"])
    assert not any(m["user_id"] == "pilot_1" for m in service._team_members["team_optics"])


def test_malformed_and_tampered_token_edge_cases(service: InvitationService):
    """Test various malformed token strings rejected with generic message."""
    malformed_tokens = [
        "",
        "   ",
        "!!!invalid_base64$$$",
        "short",
        "YWJj",  # 'abc' in base64
        "V19OT05DRV9TSE9SVA==",
        secrets.token_urlsafe(16),
        secrets.token_urlsafe(64),
    ]

    for bad_token in malformed_tokens:
        with pytest.raises(InvalidInvitationError) as exc:
            service.preview_invitation(bad_token)
        assert str(exc.value) == GENERIC_ERROR_MESSAGE


def test_full_audit_trail_logging(service: InvitationService):
    """Test comprehensive audit trail logging through entire lifecycle."""
    team_id = "team_avionics"
    req = CreateInvitationRequest(team_id=team_id, max_uses=1, role="ADMIN")

    # 1. Create
    resp = service.create_invitation(req, actor_role=TeamRole.OWNER)
    token = resp.join_url.split("/team/join/")[1]

    # 2. Preview
    service.preview_invitation(token, client_id="192.168.1.50")

    # 3. Accept (exhausting single use)
    service.accept_invitation(token, user_id="astronaut_garrus", client_id="192.168.1.50")

    # Verify audit logs
    logs = service.get_audit_logs(team_id=team_id)
    event_types = [e.event_type for e in logs]

    assert AuditEventType.TEAM_INVITATION_CREATED in event_types
    assert AuditEventType.TEAM_INVITATION_VIEWED in event_types
    assert AuditEventType.TEAM_INVITATION_ACCEPTED in event_types
    assert AuditEventType.TEAM_INVITATION_EXHAUSTED in event_types


def test_security_sanitizer_excludes_invitation_keys_and_tokens():
    """Test that SecuritySanitizer strips invitation tokens and encryption keys during .wlipjt package exports."""
    raw_project_data = {
        "project_name": "Mars Rover",
        "invitation_token": "secret_opaque_token_abc_123",
        "invitation_key": "32_byte_secret_hex_key",
        "raw_token": "raw_aes_token",
        "encryption_key": "some_secret_key",
        "public_metadata": {
            "team_name": "Rover Team",
            "version": "1.0.0",
        },
    }

    sanitized, warnings = SecuritySanitizer.sanitize_data(raw_project_data)

    assert sanitized["invitation_token"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["invitation_key"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["raw_token"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["encryption_key"] == "[REDACTED_CREDENTIAL]"
    assert sanitized["public_metadata"]["team_name"] == "Rover Team"
    assert len(warnings) >= 4


def test_token_service_nonce_collision_resistance():
    """Test that generating 500 tokens generates 500 unique nonces and unique tokens."""
    token_svc = TokenService()
    tokens = set()
    for i in range(500):
        payload = {"team_id": "team_test", "index": i}
        tok = token_svc.crypto.encrypt_payload(str(payload).encode())
        tokens.add(tok[0])  # nonce set
    assert len(tokens) == 500
