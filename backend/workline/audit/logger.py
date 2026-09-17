"""
Append-only Audit Logger with thread-safe persistence.
"""

import asyncio
from typing import List, Optional
from loguru import logger

from backend.workline.audit.models import AuditEvent


class AuditTrail:
    """Thread-safe append-only ledger for platform audit events."""

    def __init__(self):
        self._events: List[AuditEvent] = []
        self._lock = asyncio.Lock()

    async def log_event(self, event: AuditEvent) -> AuditEvent:
        async with self._lock:
            self._events.append(event)
            logger.info(f"[AuditTrail] Event logged: {event.event_type} by {event.actor_id} (Role: {event.actor_role})")
            return event

    async def get_events(
        self,
        project_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEvent]:
        async with self._lock:
            res = self._events
            if project_id:
                res = [e for e in res if e.project_id == project_id]
            if actor_id:
                res = [e for e in res if e.actor_id == actor_id]
            if event_type:
                res = [e for e in res if e.event_type == event_type]
            return res[-limit:]


default_audit_trail = AuditTrail()
