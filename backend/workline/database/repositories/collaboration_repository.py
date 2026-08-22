"""Collaboration repository for teams, members, invitations, and comments in SurrealDB."""

from typing import Dict, List, Optional
from backend.workline.database.models import (
    CommentModel,
    InvitationModel,
    TeamMemberModel,
    TeamModel,
)
from backend.workline.database.surrealdb import SurrealDBManager, surreal_db


class CollaborationRepository:
    """Repository handling team spaces, participant rosters, invites, and discussion comments."""

    def __init__(self, db: SurrealDBManager = surreal_db):
        self.db = db
        self._teams: Dict[str, TeamModel] = {}
        self._members: Dict[str, List[TeamMemberModel]] = {}
        self._invitations: Dict[str, InvitationModel] = {}
        self._comments: Dict[str, List[CommentModel]] = {}

    async def create_team(self, team: TeamModel) -> TeamModel:
        """Create team record."""
        t_id = team.id or f"team:{team.uuid}"
        team.id = t_id
        self._teams[team.uuid] = team
        self._teams[t_id] = team

        if await self.db.is_connected():
            try:
                sql = f"CREATE {t_id} CONTENT $data;"
                await self.db.query(sql, {"data": team.model_dump()})
            except Exception:
                pass

        return team

    async def get_team_by_uuid(self, uuid: str) -> Optional[TeamModel]:
        """Fetch team by 6-digit UUID."""
        return self._teams.get(uuid)

    async def add_member(self, member: TeamMemberModel) -> TeamMemberModel:
        """Add member to team."""
        m_id = member.id or f"team_member:{member.team_id}_{member.email}"
        member.id = m_id

        if member.team_id not in self._members:
            self._members[member.team_id] = []
        self._members[member.team_id].append(member)

        if await self.db.is_connected():
            try:
                sql = f"CREATE {m_id} CONTENT $data;"
                await self.db.query(sql, {"data": member.model_dump()})
            except Exception:
                pass

        return member

    async def get_members(self, team_id: str) -> List[TeamMemberModel]:
        """List team members."""
        return self._members.get(team_id, [])

    async def create_invitation(self, invitation: InvitationModel) -> InvitationModel:
        """Record a team invitation."""
        inv_id = invitation.id or f"invitation:{invitation.token_hash[:12]}"
        invitation.id = inv_id
        self._invitations[invitation.token_hash] = invitation

        if await self.db.is_connected():
            try:
                sql = f"CREATE {inv_id} CONTENT $data;"
                await self.db.query(sql, {"data": invitation.model_dump()})
            except Exception:
                pass

        return invitation

    async def add_comment(self, comment: CommentModel) -> CommentModel:
        """Post a comment on a project."""
        c_id = comment.id or f"comment:{comment.project_id}_{len(self._comments.get(comment.project_id, [])) + 1}"
        comment.id = c_id

        if comment.project_id not in self._comments:
            self._comments[comment.project_id] = []
        self._comments[comment.project_id].append(comment)

        if await self.db.is_connected():
            try:
                sql = f"CREATE {c_id} CONTENT $data;"
                await self.db.query(sql, {"data": comment.model_dump()})
            except Exception:
                pass

        return comment

    async def get_comments(self, project_id: str) -> List[CommentModel]:
        """Fetch comments for a project."""
        return self._comments.get(project_id, [])
