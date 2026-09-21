"""
Workline AI — Centralized Notification Service.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from backend.workline.collaboration.notifications.models import (
    CreateNotificationRequest,
    Notification,
    NotificationType,
)


class NotificationService:
    """Centralized notification management and event dispatching."""

    def __init__(self):
        # notification_id -> Notification
        self._notifications: Dict[str, Notification] = {}

    def send_notification(
        self,
        recipient_id: Optional[str] = None,
        type: Optional[NotificationType] = None,
        title: str = "",
        message: str = "",
        project_id: Optional[str] = None,
        related_type: Optional[str] = None,
        related_id: Optional[str] = None,
        user_id: Optional[str] = None,
        notification_type: Optional[NotificationType] = None,
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[str] = None,
    ) -> Notification:
        """Dispatches and stores a notification."""
        notif_id = f"NOTIF-{uuid.uuid4().hex[:8].upper()}"
        target_user = recipient_id or user_id or "anonymous"
        eff_type = type or notification_type or NotificationType.SYSTEM_ALERT
        r_type = related_type or related_entity_type
        r_id = related_id or related_entity_id

        notif = Notification(
            id=notif_id,
            recipient_id=target_user,
            project_id=project_id,
            type=eff_type,
            title=title,
            message=message,
            related_type=r_type,
            related_id=r_id,
            read=False,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._notifications[notif_id] = notif
        logger.info(f"[Notifications] Dispatched {eff_type.value} to {target_user}: '{title}'")
        return notif

    create_notification = send_notification

    def list_notifications(
        self,
        recipient_id: Optional[str] = None,
        user_id: Optional[str] = None,
        unread_only: bool = False,
        limit: int = 50,
    ) -> List[Notification]:
        """Retrieves notifications for a recipient sorted by creation date."""
        target = recipient_id or user_id or "all"
        results = [
            n for n in self._notifications.values()
            if n.recipient_id == target or target == "all"
        ]
        if unread_only:
            results = [n for n in results if not n.read]

        results.sort(key=lambda n: n.created_at, reverse=True)
        return results[:limit]

    def get_unread_count(self, recipient_id: str) -> int:
        """Counts unread notifications for a recipient."""
        return sum(
            1 for n in self._notifications.values()
            if (n.recipient_id == recipient_id or recipient_id == "all") and not n.read
        )

    def mark_read(self, notification_id: str, recipient_id: str) -> bool:
        """Marks a notification as read."""
        notif = self._notifications.get(notification_id)
        if notif:
            notif.read = True
            return True
        return False

    def mark_all_read(self, recipient_id: str) -> int:
        """Marks all notifications for a recipient as read."""
        count = 0
        for notif in self._notifications.values():
            if (notif.recipient_id == recipient_id or recipient_id == "all") and not notif.read:
                notif.read = True
                count += 1
        return count


# Global singleton instance
notification_service = NotificationService()
