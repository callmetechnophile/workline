"""
Workline AI — Unified Activity & Audit Service.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from backend.workline.collaboration.activity.models import (
    ActorType,
    LogActivityRequest,
    UnifiedActivityEvent,
)


class ActivityService:
    """Centralized activity and immutable audit event recorder."""

    def __init__(self):
        # event_id -> UnifiedActivityEvent
        self._events: List[UnifiedActivityEvent] = []

    def record_event(
        self,
        project_id: str,
        actor_type: ActorType,
        actor_id: str,
        actor_name: str,
        event_type: str,
        target_type: str,
        summary: str,
        target_id: Optional[str] = None,
        target_name: Optional[str] = None,
        receipt_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        team_id: Optional[str] = None,
    ) -> UnifiedActivityEvent:
        """Records an immutable activity event."""
        event_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"
        event = UnifiedActivityEvent(
            id=event_id,
            project_id=project_id,
            team_id=team_id,
            actor_type=actor_type,
            actor_id=actor_id,
            actor_name=actor_name,
            event_type=event_type,
            target_type=target_type,
            target_id=target_id,
            target_name=target_name,
            summary=summary,
            receipt_id=receipt_id,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._events.append(event)
        logger.info(
            f"[Activity] [{actor_type.value}] {actor_name} {event_type} on {target_type}:{target_id or ''} (Receipt: {receipt_id or 'none'})"
        )
        return event

    def list_events(
        self,
        project_id: Optional[str] = None,
        actor_type: Optional[ActorType] = None,
        target_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[UnifiedActivityEvent]:
        """Lists activity events with optional actor/target filters."""
        results = self._events
        if project_id:
            results = [e for e in results if e.project_id == project_id]
        if actor_type:
            results = [e for e in results if e.actor_type == actor_type]
        if target_type:
            results = [e for e in results if e.target_type == target_type.lower()]

        # Sort descending by timestamp
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]


# Global singleton instance
activity_service = ActivityService()
