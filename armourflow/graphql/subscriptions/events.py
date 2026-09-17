"""
Real-time GraphQL subscriptions for task events and system telemetry.
Integrates directly with the Control Fabric Event Bus.
"""

import asyncio
import time
from typing import Any, AsyncGenerator, Dict, Optional
import strawberry
from strawberry.scalars import JSON
from armourflow.fabric.events import get_event_bus


@strawberry.type
class FabricEventSubscriptionType:
    event_type: str
    task_id: Optional[str]
    project_id: Optional[str]
    payload: JSON
    timestamp: str


@strawberry.type
class Subscription:
    @strawberry.subscription
    async def task_updated(
        self,
        task_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> AsyncGenerator[FabricEventSubscriptionType, None]:
        """
        Stream real-time task lifecycle updates (CREATED, ROUTED, STARTED, COMPLETED, FAILED).
        Filterable by taskId and projectId.
        """
        bus = get_event_bus()
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

        def _listener(event: Dict[str, Any]):
            # Apply client filtering
            t_id = event.get("task_id")
            p_id = (event.get("data") or {}).get("project_id")
            if task_id and t_id != task_id:
                return
            if project_id and p_id != project_id:
                return
            queue.put_nowait(event)

        bus.subscribe(_listener)
        try:
            while True:
                ev = await queue.get()
                yield FabricEventSubscriptionType(
                    event_type=ev.get("event_type", "UNKNOWN"),
                    task_id=ev.get("task_id"),
                    project_id=(ev.get("data") or {}).get("project_id"),
                    payload=ev.get("data", {}),
                    timestamp=ev.get("timestamp", ""),
                )
        finally:
            if _listener in bus._subscribers:
                bus._subscribers.remove(_listener)
