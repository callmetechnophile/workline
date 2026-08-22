"""Tests for invitation creation, expiration, revocation, single/multi-use limits, and regeneration."""

from datetime import datetime, timedelta, timezone
import pytest

from backend.workline.collaboration.invitations import (
    CreateInvitationRequest,
    InvalidInvitationError,
    InvitationService,
    InvitationStatus,
    TeamRole,
)


@pytest.fixture
def clean_service() -> InvitationService:
    """Provides a fresh, isolated InvitationService instance."""
    svc = InvitationService()
    svc.register_team("team_rover", "Rover Engineering Team", owner="Alice")
    return svc


def test_invitation_creation_and_metadata(clean_service: InvitationService):
    """Test generating a secure team invitation link."""
    req = CreateInvitationRequest(
        team_id="team_rover",
        created_by="Alice",
        ttl_days=7,
        max_uses=5,
        role="ENGINEER",
    )
    resp = clean_service.create_invitation(req, actor_role=TeamRole.OWNER)

    assert resp.invitation_id.startswith("inv_")
    assert resp.team_id == "team_rover"
    assert "/team/join/" in resp.join_url
    assert resp.max_uses == 5
    assert resp.status == InvitationStatus.ACTIVE
    assert "Rover Engineering Team" in resp.message_template


def test_invitation_expiration(clean_service: InvitationService):
    """Test that expired invitations fail validation with generic error message."""
    req = CreateInvitationRequest(
        team_id="team_rover",
        created_by="Alice",
        ttl_days=1,
        max_uses=5,
    )
    resp = clean_service.create_invitation(req)
    opaque_token = resp.join_url.split("/team/join/")[1]

    # Force expiration in internal store
    inv = clean_service._invitations[resp.invitation_id]
    past_iso = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    inv.expires_at = past_iso

    with pytest.raises(InvalidInvitationError) as exc_info:
        clean_service.preview_invitation(opaque_token)
    assert str(exc_info.value) == "This invitation is invalid or no longer available."

    with pytest.raises(InvalidInvitationError):
        clean_service.accept_invitation(opaque_token, user_id="bob")


def test_invitation_revocation(clean_service: InvitationService):
    """Test revoking an active invitation."""
    req = CreateInvitationRequest(team_id="team_rover", max_uses=5)
    resp = clean_service.create_invitation(req)
    opaque_token = resp.join_url.split("/team/join/")[1]

    # Revoke
    success = clean_service.revoke_invitation(resp.invitation_id, actor_role=TeamRole.OWNER)
    assert success is True

    # Validate fails
    with pytest.raises(InvalidInvitationError):
        clean_service.preview_invitation(opaque_token)

    with pytest.raises(InvalidInvitationError):
        clean_service.accept_invitation(opaque_token, user_id="charlie")


def test_single_use_invitation(clean_service: InvitationService):
    """Test that single-use invitation (max_uses=1) exhausts after one acceptance."""
    req = CreateInvitationRequest(team_id="team_rover", max_uses=1)
    resp = clean_service.create_invitation(req)
    opaque_token = resp.join_url.split("/team/join/")[1]

    # First user joins
    res1 = clean_service.accept_invitation(opaque_token, user_id="user_1", user_name="User 1")
    assert res1.success is True
    assert res1.message == "Successfully joined team."

    # Second user attempts to use same token
    with pytest.raises(InvalidInvitationError):
        clean_service.accept_invitation(opaque_token, user_id="user_2", user_name="User 2")


def test_multi_use_invitation_and_exhaustion(clean_service: InvitationService):
    """Test multi-use invitation enforcing max_uses limit."""
    req = CreateInvitationRequest(team_id="team_rover", max_uses=3)
    resp = clean_service.create_invitation(req)
    opaque_token = resp.join_url.split("/team/join/")[1]

    # 3 users join
    for i in range(1, 4):
        res = clean_service.accept_invitation(opaque_token, user_id=f"user_{i}")
        assert res.success is True

    # 4th user must fail as exhausted
    with pytest.raises(InvalidInvitationError):
        clean_service.accept_invitation(opaque_token, user_id="user_4")


def test_regeneration_invalidates_old_token(clean_service: InvitationService):
    """Test regenerating an invitation creates a fresh link and immediately revokes the old token."""
    req = CreateInvitationRequest(team_id="team_rover", max_uses=5)
    resp1 = clean_service.create_invitation(req)
    old_token = resp1.join_url.split("/team/join/")[1]

    # Regenerate
    resp2 = clean_service.regenerate_invitation(resp1.invitation_id, actor_role=TeamRole.OWNER)
    new_token = resp2.join_url.split("/team/join/")[1]

    assert resp1.invitation_id != resp2.invitation_id
    assert old_token != new_token

    # Old token fails
    with pytest.raises(InvalidInvitationError):
        clean_service.preview_invitation(old_token)

    # New token works
    preview = clean_service.preview_invitation(new_token)
    assert preview.valid is True
    assert preview.team_name == "Rover Engineering Team"


def test_duplicate_acceptance_idempotency(clean_service: InvitationService):
    """Test that the same user accepting twice does not create duplicate memberships."""
    req = CreateInvitationRequest(team_id="team_rover", max_uses=10)
    resp = clean_service.create_invitation(req)
    token = resp.join_url.split("/team/join/")[1]

    res1 = clean_service.accept_invitation(token, user_id="engineer_bob")
    assert res1.success is True

    # Accept again
    res2 = clean_service.accept_invitation(token, user_id="engineer_bob")
    assert res2.success is True
    assert "already a member" in res2.message.lower() or "already joined" in res2.message.lower()

    # Verify members count in team
    members = clean_service._team_members["team_rover"]
    bob_members = [m for m in members if m["user_id"] == "engineer_bob"]
    assert len(bob_members) == 1
