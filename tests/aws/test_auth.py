import pytest
from fastapi import HTTPException
from backend.auth import AuthenticatedUser, require_role, _extract_unverified_claims


def test_authenticated_user_roles():
    admin = AuthenticatedUser(
        user_id="usr-1",
        roles=["system:admin"],
    )
    assert admin.has_role("system:admin")
    assert admin.has_role("project:lead")  # admin has all roles
    assert admin.has_role("viewer:read")

    engineer = AuthenticatedUser(
        user_id="usr-2",
        roles=["engineer:write"],
    )
    assert engineer.has_role("engineer:write")
    assert not engineer.has_role("system:admin")


def test_unverified_claims_extraction():
    import base64
    import json
    header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "kid": "key1"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"sub": "user-test-123", "email": "test@workline.ai"}).encode()).decode().rstrip("=")
    token = f"{header}.{payload}.signature"

    claims = _extract_unverified_claims(token)
    assert claims["sub"] == "user-test-123"
    assert claims["email"] == "test@workline.ai"


@pytest.mark.asyncio
async def test_require_role_rejection():
    role_checker = require_role("project:lead")
    viewer = AuthenticatedUser(user_id="viewer-1", roles=["viewer:read"])

    with pytest.raises(HTTPException) as exc:
        await role_checker(viewer)
    assert exc.value.status_code == 403
    assert "Insufficient privileges" in exc.value.detail
