"""Security, RBAC, secret sanitization, rate limiting, and concurrency tests for team invitations."""

from concurrent.futures import ThreadPoolExecutor
import pytest

from backend.workline.collaboration.invitations import (
    CreateInvitationRequest,
    InvalidInvitationError,
    InvitationService,
    PermissionDeniedError,
    RateLimitExceededError,
    TeamRole,
)


@pytest.fixture
def clean_service() -> InvitationService:
    svc = InvitationService()
    svc.register_team("team_sec", "Security Core Team", owner="Alice")
    return svc


def test_no_secret_leak_in_url_or_token_payload(clean_service: InvitationService):
    """Test that URLs and tokens contain zero readable secrets, passwords, or emails."""
    req = CreateInvitationRequest(
        team_id="team_sec",
        created_by="Alice",
        ttl_days=7,
        max_uses=10,
    )
    resp = clean_service.create_invitation(req)
    url = resp.join_url
    opaque_token = url.split("/team/join/")[1]

    # Verify absence of plaintext IDs and metadata in URL
    assert "team_sec" not in url
    assert "Alice" not in url
    assert "password" not in url
    assert "api_key" not in url
    assert "?" not in url  # No query parameters exposing team_id or email


def test_raw_token_and_keys_never_stored_in_database(clean_service: InvitationService):
    """Test that server-side database records store only token_hash and never the raw token."""
    req = CreateInvitationRequest(team_id="team_sec", max_uses=5)
    resp = clean_service.create_invitation(req)
    opaque_token = resp.join_url.split("/team/join/")[1]

    inv_record = clean_service._invitations[resp.invitation_id]

    # Token hash must exist
    assert inv_record.token_hash is not None
    assert len(inv_record.token_hash) == 64  # SHA-256 hex string

    # Raw token must NOT be in the model
    record_dump = inv_record.model_dump()
    assert "raw_token" not in record_dump
    assert opaque_token not in str(record_dump)


def test_rbac_unauthorized_invitation_creation_and_revocation(clean_service: InvitationService):
    """Test that only OWNER or ADMIN can create or revoke invitations."""
    req = CreateInvitationRequest(team_id="team_sec")

    # ENGINEER role cannot create
    with pytest.raises(PermissionDeniedError):
        clean_service.create_invitation(req, actor_role=TeamRole.ENGINEER)

    # VIEWER role cannot create
    with pytest.raises(PermissionDeniedError):
        clean_service.create_invitation(req, actor_role=TeamRole.VIEWER)

    # OWNER can create
    resp = clean_service.create_invitation(req, actor_role=TeamRole.OWNER)

    # VIEWER cannot revoke
    with pytest.raises(PermissionDeniedError):
        clean_service.revoke_invitation(resp.invitation_id, actor_role=TeamRole.VIEWER)


def test_rate_limiting_protects_token_guessing(clean_service: InvitationService):
    """Test that excessive preview requests trigger RateLimitExceededError."""
    # Set low limit for testing
    clean_service.validator.rate_limiter.max_requests = 5
    clean_service.validator.rate_limiter.window_seconds = 60
    clean_service.validator.rate_limiter.reset()

    req = CreateInvitationRequest(team_id="team_sec")
    resp = clean_service.create_invitation(req)
    token = resp.join_url.split("/team/join/")[1]

    # First 5 requests succeed
    for _ in range(5):
        clean_service.preview_invitation(token, client_id="attacker_ip")

    # 6th request fails with rate limit error
    with pytest.raises(RateLimitExceededError):
        clean_service.preview_invitation(token, client_id="attacker_ip")


def test_unauthenticated_preview_does_not_join_team(clean_service: InvitationService):
    """Test that previewing an invitation link does NOT automatically add user to team."""
    req = CreateInvitationRequest(team_id="team_sec", max_uses=5)
    resp = clean_service.create_invitation(req)
    token = resp.join_url.split("/team/join/")[1]

    initial_member_count = len(clean_service._team_members["team_sec"])
    preview = clean_service.preview_invitation(token, client_id="crawler_bot")

    assert preview.valid is True
    assert preview.member_count == initial_member_count

    # Check use count unchanged
    inv = clean_service._invitations[resp.invitation_id]
    assert inv.use_count == 0


def test_concurrent_invitation_acceptance(clean_service: InvitationService):
    """Test concurrent thread acceptance respecting max_uses atomically."""
    max_allowed = 4
    req = CreateInvitationRequest(team_id="team_sec", max_uses=max_allowed)
    resp = clean_service.create_invitation(req)
    token = resp.join_url.split("/team/join/")[1]

    def try_accept(user_idx: int):
        try:
            return clean_service.accept_invitation(token, user_id=f"concurrent_user_{user_idx}")
        except Exception as e:
            return e

    # 10 threads attempt simultaneous acceptance
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(try_accept, range(10)))

    successes = [r for r in results if not isinstance(r, Exception) and r.success]
    failures = [r for r in results if isinstance(r, Exception) or not getattr(r, "success", False)]

    assert len(successes) == max_allowed
    assert len(failures) == (10 - max_allowed)

    # Database state verification
    inv = clean_service._invitations[resp.invitation_id]
    assert inv.use_count == max_allowed
    assert inv.status.value == "EXHAUSTED"
