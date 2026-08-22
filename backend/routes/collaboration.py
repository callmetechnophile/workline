"""FastAPI router for Team Collaboration and Secure Team Invitations."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.armoriq.delegation import capture_plan, delegate, invoke_tool
from backend.services.collaboration_service import (
    add_comment,
    assign_role,
    create_team,
    fetch_activity_logs,
    get_project_comments,
    get_team_members,
    invite_member,
)
from backend.workline.collaboration.invitations import (
    AcceptInvitationRequest,
    AcceptInvitationResponse,
    CreateInvitationRequest,
    CreateInvitationResponse,
    InvalidInvitationError,
    InvitationPreview,
    PermissionDeniedError,
    RateLimitExceededError,
    TeamInvitation,
    TeamRole,
    invitation_service,
)

router = APIRouter(tags=["collaboration"])


class TeamCreate(BaseModel):
    name: str


class MemberInvite(BaseModel):
    team_id: int
    user_id: str
    email: str
    role: str


class RoleAssign(BaseModel):
    role: str


class CommentAdd(BaseModel):
    project_id: str
    section: str
    author: str
    content: str


class CreateInvitationBody(BaseModel):
    created_by: str = "system"
    ttl_days: int = 7
    max_uses: int = 10
    role: str = "MEMBER"


class AcceptBody(BaseModel):
    user_id: str
    user_name: Optional[str] = None


@router.post("/api/collaboration/teams")
@router.post("/api/teams")
def api_create_team(payload: TeamCreate):
    try:
        team_data = create_team(payload.name)
        # Register in invitation service
        invitation_service.register_team(str(team_data["id"]), payload.name)
        return team_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/collaboration/members")
def api_invite_member(payload: MemberInvite):
    try:
        root_receipt = capture_plan(f"Invite user {payload.user_id} to team {payload.team_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["invite_member"],
            parent_receipt=root_receipt.model_dump(),
        )
        return invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="invite_member",
            args={
                "team_id": payload.team_id,
                "user_id": payload.user_id,
                "email": payload.email,
                "role": payload.role,
            },
            receipt_dict=collab_receipt.model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/collaboration/members/{member_id}/role")
def api_assign_role(member_id: int, payload: RoleAssign):
    try:
        root_receipt = capture_plan(f"Assign role {payload.role} to member {member_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["assign_role"],
            parent_receipt=root_receipt.model_dump(),
        )
        success = invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="assign_role",
            args={"member_id": member_id, "role": payload.role},
            receipt_dict=collab_receipt.model_dump(),
        )
        if not success:
            raise HTTPException(status_code=404, detail="Member not found")
        return {"status": "SUCCESS"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/collaboration/comments")
def api_add_comment(payload: CommentAdd):
    try:
        root_receipt = capture_plan(f"Add comment to section {payload.section} of project {payload.project_id}")
        collab_receipt = delegate(
            agent_name="CollaborationAgent",
            requested_scope=["comment"],
            parent_receipt=root_receipt.model_dump(),
        )
        return invoke_tool(
            agent_name="CollaborationAgent",
            tool_name="comment",
            args={
                "project_id": payload.project_id,
                "section": payload.section,
                "author": payload.author,
                "content": payload.content,
            },
            receipt_dict=collab_receipt.model_dump(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/collaboration/comments/{project_id}")
def api_get_comments(project_id: str):
    try:
        return get_project_comments(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/collaboration/members/{team_id}")
def api_get_members(team_id: int):
    try:
        return get_team_members(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/collaboration/activity/{team_id}")
def api_fetch_activity(team_id: int):
    try:
        return fetch_activity_logs(team_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# SECURE TEAM INVITATION ENDPOINTS (AES-256-GCM)
# ============================================================


@router.post("/api/teams/{team_id}/invitations", response_model=CreateInvitationResponse)
@router.post("/api/collaboration/teams/{team_id}/invitations", response_model=CreateInvitationResponse)
def api_create_team_invitation(team_id: str, payload: CreateInvitationBody):
    """Generates an opaque, authenticated AES-256-GCM encrypted invitation link."""
    try:
        req = CreateInvitationRequest(
            team_id=str(team_id),
            created_by=payload.created_by,
            ttl_days=payload.ttl_days,
            max_uses=payload.max_uses,
            role=payload.role,
        )
        return invitation_service.create_invitation(req, actor_role=TeamRole.OWNER)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/teams/{team_id}/invitations", response_model=List[TeamInvitation])
@router.get("/api/collaboration/teams/{team_id}/invitations", response_model=List[TeamInvitation])
def api_list_team_invitations(team_id: str):
    """Lists all active and historical invitations for a team (without raw tokens)."""
    try:
        return invitation_service.list_invitations(str(team_id), actor_role=TeamRole.OWNER)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/teams/{team_id}/invitations/{invitation_id}/revoke")
@router.post("/api/collaboration/teams/{team_id}/invitations/{invitation_id}/revoke")
def api_revoke_team_invitation(team_id: str, invitation_id: str):
    """Revokes an active invitation link immediately."""
    try:
        success = invitation_service.revoke_invitation(invitation_id, actor_role=TeamRole.OWNER)
        if not success:
            raise HTTPException(status_code=404, detail="Invitation not found.")
        return {"status": "REVOKED", "invitation_id": invitation_id}
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/teams/{team_id}/invitations/{invitation_id}/regenerate", response_model=CreateInvitationResponse)
@router.post("/api/collaboration/teams/{team_id}/invitations/{invitation_id}/regenerate", response_model=CreateInvitationResponse)
def api_regenerate_team_invitation(team_id: str, invitation_id: str):
    """Revokes the existing invitation and returns a freshly encrypted token link."""
    try:
        return invitation_service.regenerate_invitation(invitation_id, actor_role=TeamRole.OWNER)
    except PermissionDeniedError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except InvalidInvitationError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/invitations/{token}/preview", response_model=InvitationPreview)
@router.get("/api/collaboration/invitations/{token}/preview", response_model=InvitationPreview)
@router.get("/api/collaboration/invitations/{token}")
def api_preview_invitation(token: str, request: Request):
    """
    Validates token and returns safe pre-join team preview.
    Does not automatically join the team or expose private secrets.
    """
    client_ip = request.client.host if request.client else "unknown"
    try:
        return invitation_service.preview_invitation(token, client_id=client_ip)
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidInvitationError:
        raise HTTPException(status_code=404, detail="This invitation is invalid or no longer available.")
    except Exception:
        raise HTTPException(status_code=404, detail="This invitation is invalid or no longer available.")


@router.post("/api/invitations/{token}/accept", response_model=AcceptInvitationResponse)
@router.post("/api/collaboration/invitations/{token}/accept", response_model=AcceptInvitationResponse)
def api_accept_invitation(token: str, payload: AcceptBody, request: Request):
    """
    Accepts invitation link and establishes team membership.
    Enforces rate limiting, expiration, revocation, and atomic usage thresholds.
    """
    client_ip = request.client.host if request.client else payload.user_id
    try:
        return invitation_service.accept_invitation(
            opaque_token=token,
            user_id=payload.user_id,
            user_name=payload.user_name,
            client_id=client_ip,
        )
    except RateLimitExceededError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except InvalidInvitationError:
        raise HTTPException(status_code=400, detail="This invitation is invalid or no longer available.")
    except Exception:
        raise HTTPException(status_code=400, detail="This invitation is invalid or no longer available.")
