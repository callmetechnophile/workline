"""Append-only audit trail logger for Workline order, payment, and execution events."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from cli.wline.core.paths import get_config_dir
from backend.workline.database.models import GraphNode
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.orders.models import AuditEventType, OrderAuditEvent


class OrderAuditLogger:
    """Immutable, append-only logger maintaining complete provenance for financial and order events."""

    def __init__(self, graph_repo: Optional[GraphRepository] = None):
        self.graph_repo = graph_repo or GraphRepository()
        self._events: List[OrderAuditEvent] = []
        self._audit_dir = get_config_dir() / "audit" / "orders"
        self._audit_dir.mkdir(parents=True, exist_ok=True)

    async def log_event(
        self,
        order_id: str,
        project_id: str,
        event_type: AuditEventType,
        user_id: str = "user:engineer",
        team_id: str = "team:default",
        actor_type: str = "USER",
        actor_id: str = "user:engineer",
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OrderAuditEvent:
        """Create and append an immutable audit event."""
        event = OrderAuditEvent(
            event_id=f"audit_{uuid.uuid4().hex[:12]}",
            order_id=order_id,
            project_id=project_id,
            user_id=user_id,
            team_id=team_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            actor_type=actor_type,
            actor_id=actor_id,
            previous_status=previous_status,
            new_status=new_status,
            metadata=metadata or {},
        )

        # 1. Append in memory
        self._events.append(event)

        # 2. Append to disk (JSON lines format)
        try:
            order_file = self._audit_dir / f"{order_id.replace(':', '_')}.jsonl"
            with open(order_file, "a", encoding="utf-8") as fp:
                fp.write(event.model_dump_json() + "\n")
        except Exception:
            pass

        # 3. Persist to SurrealDB
        try:
            node = GraphNode(
                id=event.event_id,
                type="OrderAuditEvent",
                label=f"{event.event_type.value} ({event.order_id})",
                data=event.model_dump(),
            )
            await self.graph_repo.save_node(node)
        except Exception:
            pass

        return event

    def get_order_events(self, order_id: str) -> List[OrderAuditEvent]:
        """Fetch chronological audit history for an order."""
        # Check memory
        mem_events = [e for e in self._events if e.order_id == order_id]
        if mem_events:
            return sorted(mem_events, key=lambda x: x.timestamp)

        # Check disk
        order_file = self._audit_dir / f"{order_id.replace(':', '_')}.jsonl"
        disk_events: List[OrderAuditEvent] = []
        if order_file.exists():
            try:
                with open(order_file, "r", encoding="utf-8") as fp:
                    for line in fp:
                        if line.strip():
                            disk_events.append(OrderAuditEvent.model_validate_json(line))
            except Exception:
                pass
        return sorted(disk_events, key=lambda x: x.timestamp)


# Singleton Audit Logger
order_audit_logger = OrderAuditLogger()
