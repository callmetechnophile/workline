"""
Workline AI — Teams & Collaboration API Router.

Exposes REST endpoints for:
1. Team creation & member management.
2. Secure 6-character CSPRNG join code lifecycle (Join, Rotate, Revoke).
3. RSA-OAEP asymmetric encryption & RSA-PSS cryptographic signing of invitations.
4. Rate-limited join attempts and enumeration-protected generic error handling.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from backend.workline.collaboration.crypto.rsa import rsa_engine
from backend.workline.collaboration.teams.models import (
    CreateTeamRequest,
    CreateTeamResponse,
    JoinTeamRequest,
    JoinTeamResponse,
    RevokeJoinCodeResponse,
    RotateJoinCodeResponse,
    Team,
    TeamRole,
    UpdateMemberRoleRequest,
)
from backend.workline.collaboration.teams.service import (
    InvalidJoinCodeError,
    PermissionDeniedError,
    RateLimitExceededError,
    TeamNotFoundError,
    team_service,
)

router = APIRouter(prefix="/api/teams", tags=["teams"])


def get_current_user_id(x_user_id: Optional[str] = Header(None, alias="X-User-Id")) -> Optional[str]:
    """Extracts authenticated user ID from headers."""
    if x_user_id is not None:
        clean = x_user_id.strip()
        return clean if clean else None
    return "user_default_owner"


# ---------------------------------------------------------------------------
# Team CRUD & Join Flow
# ---------------------------------------------------------------------------

@router.post("", response_model=CreateTeamResponse)
def create_team(
    payload: CreateTeamRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Creates a new team, designates creator as OWNER, and returns 6-char join code once."""
    user_id = get_current_user_id(x_user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    try:
        return team_service.create_team(
            name=payload.name,
            creator_user_id=user_id,
            description=payload.description or "",
            request_id=request.headers.get("X-Request-Id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create team: {str(e)}")


@router.get("", response_model=List[Dict[str, Any]])
def list_teams(x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Lists all teams the authenticated user belongs to."""
    user_id = get_current_user_id(x_user_id)
    return team_service.list_user_teams(user_id)


@router.get("/{team_id}", response_model=Team)
def get_team(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Gets team details for an active member."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.get_team(team_id, user_id)
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail="Access denied: You are not a member of this team.")


@router.post("/join", response_model=JoinTeamResponse)
def join_team(
    payload: JoinTeamRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Joins an existing team via 6-character alphanumeric join code.
    Protected by HMAC verification, expiration checks, and brute-force rate limiting.
    """
    user_id = get_current_user_id(x_user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    client_ip = request.client.host if request.client else "unknown"

    try:
        return team_service.join_team(
            raw_code=payload.code,
            user_id=user_id,
            client_ip=client_ip,
            request_id=request.headers.get("X-Request-Id"),
        )
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidJoinCodeError:
        # Intentionally generic error to prevent team enumeration
        raise HTTPException(status_code=400, detail="Invalid or expired team code.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred while joining the team.")


# ---------------------------------------------------------------------------
# Code Rotation & Revocation
# ---------------------------------------------------------------------------

@router.post("/{team_id}/join-code/rotate", response_model=RotateJoinCodeResponse)
def rotate_join_code(
    team_id: str,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Rotates team join code (Owner/Admin only). Revokes previous code permanently."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.rotate_join_code(
            team_id=team_id,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{team_id}/join-code/revoke", response_model=RevokeJoinCodeResponse)
def revoke_join_code(
    team_id: str,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Revokes active team join code immediately (Owner/Admin only)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.revoke_join_code(
            team_id=team_id,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---------------------------------------------------------------------------
# Member Management
# ---------------------------------------------------------------------------

@router.get("/{team_id}/members", response_model=List[Dict[str, Any]])
def list_team_members(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Lists members for a team."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.list_members(team_id, user_id)
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.put("/{team_id}/members/{target_user_id}/role")
def update_member_role(
    team_id: str,
    target_user_id: str,
    payload: UpdateMemberRoleRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Updates a team member's role (Owner/Admin only with owner protections)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.update_member_role(
            team_id=team_id,
            target_user_id=target_user_id,
            new_role=payload.role,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except (TeamNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{team_id}/members/{target_user_id}")
def remove_member(
    team_id: str,
    target_user_id: str,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Removes a member from the team (Owner/Admin only, cannot remove owner)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.remove_member(
            team_id=team_id,
            target_user_id=target_user_id,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except (TeamNotFoundError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/{team_id}/activity", response_model=List[Dict[str, Any]])
def get_team_activity(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Retrieves immutable audit trail for team operations."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.get_audit_logs(team_id, user_id)
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---------------------------------------------------------------------------
# RSA Asymmetric Cryptography Payloads (RSA-OAEP & RSA-PSS)
# ---------------------------------------------------------------------------

class RsaEncryptRequest(BaseModel):
    payload: Dict[str, Any]
    recipient_public_key_pem: Optional[str] = None


class RsaDecryptRequest(BaseModel):
    ciphertext: str


class RsaSignRequest(BaseModel):
    payload: Dict[str, Any]


class RsaVerifyRequest(BaseModel):
    payload: Dict[str, Any]
    signature: str
    signer_public_key_pem: Optional[str] = None


@router.post("/crypto/rsa/public-key")
def get_rsa_public_key():
    """Returns the server's public RSA key in PEM format."""
    return {"public_key": rsa_engine.get_public_key_pem()}


@router.post("/{team_id}/invitations/encrypted")
def create_rsa_encrypted_invitation(
    team_id: str,
    payload: RsaEncryptRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Encrypts invitation payload using RSA-OAEP + SHA-256."""
    user_id = get_current_user_id(x_user_id)
    team_service.get_team(team_id, user_id)
    ciphertext = rsa_engine.encrypt_payload(payload.payload, payload.recipient_public_key_pem)
    return {"ciphertext": ciphertext, "algorithm": "RSA-OAEP-SHA256"}


@router.post("/{team_id}/invitations/signed")
def create_rsa_signed_invitation(
    team_id: str,
    payload: RsaSignRequest,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Signs invitation metadata using RSA-PSS + SHA-256."""
    user_id = get_current_user_id(x_user_id)
    team_service.get_team(team_id, user_id)
    signature = rsa_engine.sign_payload(payload.payload)
    return {"signature": signature, "algorithm": "RSA-PSS-SHA256"}


@router.post("/invitations/verify-signed")
def verify_rsa_signed_invitation(payload: RsaVerifyRequest):
    """Verifies RSA-PSS + SHA-256 signature."""
    valid = rsa_engine.verify_signature(
        data=payload.payload,
        b64_signature=payload.signature,
        public_key_pem=payload.signer_public_key_pem,
    )
    return {"valid": valid}


@router.post("/invitations/decrypt")
def decrypt_rsa_invitation(payload: RsaDecryptRequest):
    """Decrypts RSA-OAEP + SHA-256 payload with server private key."""
    try:
        data = rsa_engine.decrypt_payload(payload.ciphertext)
        return {"payload": data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {str(e)}")
