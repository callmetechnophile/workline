"""
Workline AI — Teams & Collaboration API Router.

Exposes REST endpoints for:
1. Team creation & member management with 5-tier roles.
2. Secure 'WL-XXXXXX' join code lifecycle (Preview, Join, Rotate, Revoke).
3. Membership request approval flow (require_join_approval).
4. Protected ownership transfer protocol.
5. RSA-OAEP asymmetric encryption & RSA-PSS cryptographic signing of invitations.
6. Rate-limited join attempts and enumeration-protected generic error handling.
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
    MembershipRequest,
    ReviewMembershipRequest,
    RevokeJoinCodeResponse,
    RotateJoinCodeResponse,
    Team,
    TeamPreviewResponse,
    TeamRole,
    TransferOwnershipRequest,
    UpdateMemberRoleRequest,
    UpdateTeamSettingsRequest,
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
    """Creates a new team, designates creator as OWNER, and returns WL-XXXXXX join code once."""
    user_id = get_current_user_id(x_user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    try:
        return team_service.create_team(
            name=payload.name,
            creator_user_id=user_id,
            description=payload.description or "",
            project_id=payload.project_id,
            require_join_approval=payload.require_join_approval or False,
            default_join_role=payload.default_join_role or TeamRole.ENGINEER,
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


@router.get("/preview-code/{code}", response_model=TeamPreviewResponse)
def preview_join_code(code: str, request: Request):
    """Safe metadata preview for a WL-XXXXXX join code without joining."""
    client_ip = request.client.host if request.client else "unknown"
    try:
        return team_service.preview_join_code(raw_code=code, client_ip=client_ip)
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidJoinCodeError:
        raise HTTPException(status_code=404, detail="Invalid or expired team code.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/join", response_model=JoinTeamResponse)
def join_team(
    payload: JoinTeamRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """
    Joins an existing team via WL-XXXXXX code.
    Protected by HMAC verification, expiration checks, and brute-force rate limiting.
    Creates a MembershipRequest if require_join_approval is enabled.
    """
    user_id = get_current_user_id(x_user_id)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required.")

    client_ip = request.client.host if request.client else "unknown"

    try:
        return team_service.join_team(
            raw_code=payload.code,
            user_id=user_id,
            requested_role=payload.requested_role,
            user_name=payload.user_name,
            user_email=payload.user_email,
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
        raise HTTPException(status_code=500, detail=f"An error occurred while joining the team: {str(e)}")


# ---------------------------------------------------------------------------
# Membership Requests
# ---------------------------------------------------------------------------

@router.get("/{team_id}/membership-requests", response_model=List[MembershipRequest])
def list_membership_requests(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Lists pending membership requests (Owner/Admin only)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.list_membership_requests(team_id, user_id)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{team_id}/membership-requests/{request_id}/review")
def review_membership_request(
    team_id: str,
    request_id: str,
    payload: ReviewMembershipRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Approves or rejects a membership request (Owner/Admin only)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.review_membership_request(
            request_id=request_id,
            action=payload.action,
            actor_user_id=user_id,
            assigned_role=payload.assigned_role,
            reason=payload.reason,
            request_id_header=request.headers.get("X-Request-Id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
# Member & Role Management
# ---------------------------------------------------------------------------

@router.get("/{team_id}/members", response_model=List[Dict[str, Any]])
def list_members(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Lists all active members of a team."""
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
    """Updates role for a member with strict owner protection."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.update_member_role(
            team_id=team_id,
            target_user_id=target_user_id,
            new_role=payload.role,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{team_id}/members/{target_user_id}")
def remove_member(
    team_id: str,
    target_user_id: str,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Removes a member from the team. Prevents removing the sole OWNER."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.remove_member(
            team_id=team_id,
            target_user_id=target_user_id,
            actor_user_id=user_id,
            request_id=request.headers.get("X-Request-Id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


# ---------------------------------------------------------------------------
# Ownership Transfer & Settings
# ---------------------------------------------------------------------------

@router.post("/{team_id}/transfer-ownership")
def transfer_ownership(
    team_id: str,
    payload: TransferOwnershipRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Securely transfers team ownership with confirmation phrase (Owner only)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.transfer_ownership(
            team_id=team_id,
            target_user_id=payload.target_user_id,
            actor_user_id=user_id,
            confirmation_phrase=payload.confirmation_phrase,
            request_id=request.headers.get("X-Request-Id"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.patch("/{team_id}/settings", response_model=Team)
def update_team_settings(
    team_id: str,
    payload: UpdateTeamSettingsRequest,
    request: Request,
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
):
    """Updates team settings (Owner/Admin only)."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.update_team_settings(
            team_id=team_id,
            actor_user_id=user_id,
            name=payload.name,
            description=payload.description,
            require_join_approval=payload.require_join_approval,
            default_join_role=payload.default_join_role,
            request_id=request.headers.get("X-Request-Id"),
        )
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------

@router.get("/{team_id}/activity", response_model=List[Dict[str, Any]])
def get_team_activity(team_id: str, x_user_id: Optional[str] = Header(None, alias="X-User-Id")):
    """Retrieves immutable audit trail for a team."""
    user_id = get_current_user_id(x_user_id)
    try:
        return team_service.get_audit_logs(team_id, user_id)
    except TeamNotFoundError:
        raise HTTPException(status_code=404, detail="Team not found.")
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
