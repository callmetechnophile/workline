"""
Workline AI — Contextual Comments & Mentions Service.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from backend.workline.collaboration.comments.models import (
    ContextComment,
    CreateCommentRequest,
    UpdateCommentRequest,
)

MENTION_REGEX = re.compile(r"@([\w\.\-]+)")


class CommentService:
    """Service managing contextual comments on engineering artifacts and project entities."""

    def __init__(self):
        # comment_id -> ContextComment
        self._comments: Dict[str, ContextComment] = {}

    def extract_mentions(self, text: str) -> List[str]:
        """Extracts @mentions from comment body."""
        return list(set(MENTION_REGEX.findall(text)))

    def add_comment(
        self,
        payload: CreateCommentRequest,
        author_id: str,
        author_name: str,
    ) -> ContextComment:
        """Adds a comment, extracts mentions, and stores it."""
        comment_id = f"CMT-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()
        mentions = self.extract_mentions(payload.content)

        comment = ContextComment(
            id=comment_id,
            project_id=payload.project_id,
            parent_type=(payload.parent_type or "project").lower(),
            parent_id=payload.parent_id or "general",
            author_id=author_id,
            author_name=author_name or author_id,
            content=payload.content.strip(),
            mentions=mentions,
            reply_to_id=payload.reply_to_id,
            created_at=now,
            updated_at=now,
            is_edited=False,
            is_deleted=False,
        )
        self._comments[comment_id] = comment
        logger.info(
            f"[Comments] Created comment {comment_id} on {comment.parent_type}:{comment.parent_id} by {author_id}"
        )

        # Notify mentioned users
        for m_user in mentions:
            try:
                from backend.workline.collaboration.notifications.models import NotificationType
                from backend.workline.collaboration.notifications.service import notification_service
                notification_service.create_notification(
                    user_id=m_user,
                    notification_type=NotificationType.MENTION,
                    title=f"{author_name or author_id} mentioned you",
                    message=f"In {comment.parent_type}:{comment.parent_id}: {payload.content[:120]}",
                    related_entity_type=comment.parent_type,
                    related_entity_id=comment.parent_id,
                )
            except Exception:
                pass

        return comment

    create_comment = add_comment

    def get_comments(
        self,
        project_id: str,
        parent_type: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> List[ContextComment]:
        """Retrieves comments for a project, optionally filtered by artifact parent."""
        results = [
            c for c in self._comments.values()
            if c.project_id == project_id and not c.is_deleted
        ]
        if parent_type:
            results = [c for c in results if c.parent_type == parent_type.lower()]
        if parent_id:
            results = [c for c in results if c.parent_id == parent_id]

        results.sort(key=lambda c: c.created_at)
        return results

    def update_comment(
        self,
        comment_id: str,
        payload: UpdateCommentRequest,
        actor_id: str,
    ) -> ContextComment:
        """Updates a comment body."""
        comment = self._comments.get(comment_id)
        if not comment or comment.is_deleted:
            raise ValueError("Comment not found.")

        if comment.author_id != actor_id:
            raise PermissionError("You can only edit your own comments.")

        now = datetime.now(timezone.utc).isoformat()
        comment.content = payload.content.strip()
        comment.mentions = self.extract_mentions(comment.content)
        comment.updated_at = now
        comment.is_edited = True
        return comment

    def delete_comment(self, comment_id: str, actor_id: str, is_admin: bool = False) -> bool:
        """Soft-deletes a comment."""
        comment = self._comments.get(comment_id)
        if not comment or comment.is_deleted:
            return False

        if comment.author_id != actor_id and not is_admin:
            raise PermissionError("You do not have permission to delete this comment.")

        comment.is_deleted = True
        comment.content = "[Comment deleted by author or administrator]"
        comment.updated_at = datetime.now(timezone.utc).isoformat()
        return True


# Global singleton instance
comment_service = CommentService()
