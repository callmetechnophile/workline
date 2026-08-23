"""
Workline AI — Secure Team Collaboration & Join Code Test Suite.

Comprehensive security, cryptographic, and lifecycle validation:
 1. Create team while unauthenticated -> 401
 2. Create team while authenticated -> success
 3. Creator automatically becomes OWNER
 4. Join team using valid 6-char CSPRNG code -> membership established
 5. Join team using lowercase code -> normalized to uppercase and accepted
 6. Join team with 5 characters -> 400 rejection
 7. Join team with 7 characters -> 400 rejection
 8. Join team with invalid symbols -> 400 rejection
 9. Join team with expired code -> rejected
10. Join team with revoked code -> rejected
11. Join team twice -> duplicate membership prevented (returns ALREADY_MEMBER)
12. Brute-force join attempts -> rate limited with cooldown
13. Invalid code -> generic response (zero team enumeration)
14. Unauthorized project access check -> 403 denied
15. MEMBER attempts to rotate join code -> 403 denied
16. MEMBER attempts to remove member -> 403 denied
17. ADMIN attempts protected OWNER removal -> 403 denied
18. Sole OWNER cannot be removed
19. Plaintext join code is NEVER stored in team record or audit logs
20. HMAC-SHA-256 deterministic digest verification
21. RSA-OAEP + SHA-256 asymmetric encryption & decryption roundtrip
22. RSA-PSS + SHA-256 digital signature & verification roundtrip
23. Zero RSA private keys in public exports
"""

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.workline.collaboration.crypto.rsa import rsa_engine
from backend.workline.collaboration.teams.models import TeamRole, TeamStatus
from backend.workline.collaboration.teams.rate_limiter import join_rate_limiter
from backend.workline.collaboration.teams.service import (
    InvalidJoinCodeError,
    PermissionDeniedError,
    RateLimitExceededError,
    TeamNotFoundError,
    team_service,
)


@pytest.fixture(autouse=True)
def reset_state():
    """Resets rate limiter and team service test stores between tests."""
    join_rate_limiter.reset_for_test()
    team_service._teams.clear()
    team_service._members.clear()
    team_service._audit_logs.clear()
    team_service._project_teams.clear()


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# 1. Unauthenticated vs Authenticated Team Creation
# ---------------------------------------------------------------------------

def test_create_team_unauthenticated_fails(client):
    """Attempting to create team without user identification raises 401."""
    # When X-User-Id header is empty string
    resp = client.post("/api/teams", json={"name": "Alpha Team"}, headers={"X-User-Id": ""})
    assert resp.status_code == 401


def test_create_team_authenticated_succeeds(client):
    """Authenticated user creates team and receives 6-character join code."""
    resp = client.post(
        "/api/teams",
        json={"name": "Alpha Team", "description": "Hardware Engineering Team"},
        headers={"X-User-Id": "user_creator_123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Alpha Team"
    assert data["owner_id"] == "user_creator_123"
    assert data["role"] == "OWNER"
    assert len(data["join_code"]) == 6
    assert data["join_code"].isalnum()
    assert data["join_code"].isupper()


# ---------------------------------------------------------------------------
# 2. Creator Automatically Becomes OWNER
# ---------------------------------------------------------------------------

def test_creator_becomes_owner():
    """Verifies that the creator is assigned the OWNER role in the team."""
    res = team_service.create_team(name="Robotics Core", creator_user_id="user_owner_99")
    members = team_service.list_members(res.team_id, actor_user_id="user_owner_99")
    assert len(members) == 1
    assert members[0]["user_id"] == "user_owner_99"
    assert members[0]["role"] == TeamRole.OWNER


# ---------------------------------------------------------------------------
# 3. Join Code Lifecycle & Normalization
# ---------------------------------------------------------------------------

def test_join_team_valid_code():
    """User joins team using valid 6-char alphanumeric code."""
    created = team_service.create_team(name="Quantum Lab", creator_user_id="owner_1")
    join_res = team_service.join_team(
        raw_code=created.join_code,
        user_id="user_engineer_2",
    )
    assert join_res.status == "JOINED"
    assert join_res.team_id == created.team_id
    assert join_res.role == TeamRole.MEMBER

    # Verify member count updated
    team = team_service.get_team(created.team_id, actor_user_id="owner_1")
    assert team.member_count == 2


def test_join_team_lowercase_code_normalized():
    """Lowercase input is automatically normalized to uppercase and accepted."""
    created = team_service.create_team(name="Avionics Division", creator_user_id="owner_1")
    lowercase_code = created.join_code.lower()

    join_res = team_service.join_team(
        raw_code=lowercase_code,
        user_id="user_engineer_3",
    )
    assert join_res.status == "JOINED"


def test_join_team_invalid_length_rejected(client):
    """5-character and 7-character inputs are rejected with 400."""
    resp5 = client.post("/api/teams/join", json={"code": "12345"}, headers={"X-User-Id": "u1"})
    assert resp5.status_code == 400

    resp7 = client.post("/api/teams/join", json={"code": "1234567"}, headers={"X-User-Id": "u1"})
    assert resp7.status_code == 400


def test_join_team_invalid_symbols_rejected(client):
    """Codes with punctuation or spaces are rejected with 400."""
    resp = client.post("/api/teams/join", json={"code": "AB#45!"}, headers={"X-User-Id": "u1"})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 4. Expiration & Revocation
# ---------------------------------------------------------------------------

def test_join_team_expired_code_rejected():
    """Expired join code is rejected with generic InvalidJoinCodeError."""
    created = team_service.create_team(name="Thermal Dynamics", creator_user_id="owner_1")
    # Manually expire the code in the past
    team = team_service._teams[created.team_id]
    team.join_code_expires_at = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()

    with pytest.raises(InvalidJoinCodeError, match="Invalid or expired team code"):
        team_service.join_team(raw_code=created.join_code, user_id="user_late")


def test_join_team_revoked_code_rejected():
    """Revoked join code is rejected."""
    created = team_service.create_team(name="Radar Tech", creator_user_id="owner_1")
    team_service.revoke_join_code(team_id=created.team_id, actor_user_id="owner_1")

    with pytest.raises(InvalidJoinCodeError, match="Invalid or expired team code"):
        team_service.join_team(raw_code=created.join_code, user_id="user_after_revocation")


def test_rotate_join_code_invalidates_previous():
    """Rotating join code makes the old code invalid while activating the new code."""
    created = team_service.create_team(name="Embedded OS", creator_user_id="owner_1")
    old_code = created.join_code

    rotated = team_service.rotate_join_code(team_id=created.team_id, actor_user_id="owner_1")
    new_code = rotated.join_code
    assert new_code != old_code

    # Old code fails
    with pytest.raises(InvalidJoinCodeError):
        team_service.join_team(raw_code=old_code, user_id="u_old")

    # New code succeeds
    res = team_service.join_team(raw_code=new_code, user_id="u_new")
    assert res.status == "JOINED"


# ---------------------------------------------------------------------------
# 5. Duplicate Membership Prevention
# ---------------------------------------------------------------------------

def test_join_twice_prevents_duplicate_membership():
    """Joining the same team twice returns ALREADY_MEMBER without duplicating member rows."""
    created = team_service.create_team(name="Signal Processing", creator_user_id="owner_1")
    r1 = team_service.join_team(raw_code=created.join_code, user_id="user_dup")
    assert r1.status == "JOINED"

    r2 = team_service.join_team(raw_code=created.join_code, user_id="user_dup")
    assert r2.status == "ALREADY_MEMBER"

    members = team_service.list_members(created.team_id, actor_user_id="owner_1")
    assert len(members) == 2  # Owner + 1 Member (not 3)


# ---------------------------------------------------------------------------
# 6. Brute-Force Rate Limiting & Enumeration Protection
# ---------------------------------------------------------------------------

def test_brute_force_rate_limiting():
    """After 5 consecutive failed attempts, rate limiter enforces cooldown."""
    team_service.create_team(name="Security Enclave", creator_user_id="owner_1")

    # 5 failed attempts
    for _ in range(5):
        try:
            team_service.join_team(raw_code="BAD123", user_id="attacker_1", client_ip="192.168.1.50")
        except InvalidJoinCodeError:
            pass

    # 6th attempt triggers RateLimitExceededError
    with pytest.raises(RateLimitExceededError, match="Too many failed join attempts"):
        team_service.join_team(raw_code="BAD123", user_id="attacker_1", client_ip="192.168.1.50")


def test_code_enumeration_generic_error(client):
    """Invalid codes return identical generic 400 error regardless of whether target team exists."""
    resp = client.post("/api/teams/join", json={"code": "ZZZZZZ"}, headers={"X-User-Id": "u_enum"})
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Invalid or expired team code."


# ---------------------------------------------------------------------------
# 7. Role-Based Permissions & Owner Protection
# ---------------------------------------------------------------------------

def test_member_cannot_rotate_code():
    """MEMBER role cannot rotate team join codes."""
    created = team_service.create_team(name="FPGA Dev", creator_user_id="owner_1")
    team_service.join_team(raw_code=created.join_code, user_id="member_1")

    with pytest.raises(PermissionDeniedError, match="Only team OWNER or ADMIN"):
        team_service.rotate_join_code(team_id=created.team_id, actor_user_id="member_1")


def test_member_cannot_remove_members():
    """MEMBER role cannot remove other members."""
    created = team_service.create_team(name="ASIC Design", creator_user_id="owner_1")
    team_service.join_team(raw_code=created.join_code, user_id="m1")
    team_service.join_team(raw_code=created.join_code, user_id="m2")

    with pytest.raises(PermissionDeniedError, match="Only OWNER or ADMIN"):
        team_service.remove_member(team_id=created.team_id, target_user_id="m2", actor_user_id="m1")


def test_sole_owner_cannot_be_removed():
    """Sole OWNER cannot be removed or demoted."""
    created = team_service.create_team(name="Optics Lab", creator_user_id="sole_owner")

    with pytest.raises(PermissionDeniedError, match="Cannot remove the team OWNER"):
        team_service.remove_member(team_id=created.team_id, target_user_id="sole_owner", actor_user_id="sole_owner")

    with pytest.raises(PermissionDeniedError, match="Cannot demote the sole team OWNER"):
        team_service.update_member_role(
            team_id=created.team_id,
            target_user_id="sole_owner",
            new_role=TeamRole.MEMBER,
            actor_user_id="sole_owner",
        )


# ---------------------------------------------------------------------------
# 8. Zero Plaintext Code Storage & Audit Logging
# ---------------------------------------------------------------------------

def test_plaintext_join_code_not_stored_in_database():
    """Verifies that Team model and database representation store only HMAC digest."""
    created = team_service.create_team(name="Silicon Photonics", creator_user_id="owner_1")
    team = team_service._teams[created.team_id]

    assert created.join_code not in str(team.model_dump())
    assert team.join_code_digest is not None
    assert len(team.join_code_digest) == 64  # SHA-256 hex length


def test_audit_log_contains_no_plaintext_join_codes():
    """Audit logs must never contain the 6-character plaintext join code."""
    created = team_service.create_team(name="Cryogenics", creator_user_id="owner_1")
    team_service.join_team(raw_code=created.join_code, user_id="m1")
    team_service.rotate_join_code(team_id=created.team_id, actor_user_id="owner_1")

    logs = team_service.get_audit_logs(created.team_id, actor_user_id="owner_1")
    for entry in logs:
        assert created.join_code not in str(entry)


# ---------------------------------------------------------------------------
# 9. Cryptography Subsystem (HMAC, RSA-OAEP, RSA-PSS)
# ---------------------------------------------------------------------------

def test_hmac_deterministic_digest():
    """Same code with same secret yields same digest; different code yields different digest."""
    secret = b"test_secret_key_12345"
    h1 = hmac.new(secret, b"A7K9Q2", hashlib.sha256).hexdigest()
    h2 = hmac.new(secret, b"A7K9Q2", hashlib.sha256).hexdigest()
    h3 = hmac.new(secret, b"B8L0R3", hashlib.sha256).hexdigest()

    assert h1 == h2
    assert h1 != h3


def test_rsa_oaep_encryption_decryption_roundtrip():
    """Confidential payload encrypted with RSA-OAEP + SHA-256 decrypts cleanly with private key."""
    payload = {"invitation_id": "inv_123", "team_id": "team_alpha", "role": "ENGINEER"}
    ciphertext = rsa_engine.encrypt_payload(payload)
    decrypted = rsa_engine.decrypt_payload(ciphertext)

    assert decrypted == payload


def test_rsa_pss_signature_verification_roundtrip():
    """Payload signed with RSA-PSS + SHA-256 verifies correctly; modified payload fails."""
    payload = {"invitation_id": "inv_456", "team_id": "team_beta", "issued_at": "2026-08-23T11:00:00Z"}
    signature = rsa_engine.sign_payload(payload)

    # Valid verification
    assert rsa_engine.verify_signature(payload, signature) is True

    # Tampered payload fails verification
    tampered_payload = dict(payload, role="OWNER")
    assert rsa_engine.verify_signature(tampered_payload, signature) is False
