"""Lightweight event publisher/subscriber for the Control Fabric."""

import asyncio
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from loguru import logger


class FabricEventBus:
    """In-process asynchronous event bus for task state and execution telemetry."""

    def __init__(self):
        self._subscribers: List[Callable[[Dict[str, Any]], None]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], None]):
        self._subscribers.append(callback)

    def publish(self, event_type: str, task_id: str, data: Dict[str, Any]):
        evt = {
            "event_type": event_type,
            "task_id": task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        for sub in self._subscribers:
            try:
                sub(evt)
            except Exception as e:
                logger.warning(f"[FabricEventBus] Error in subscriber: {e}")


_bus_instance: Optional[FabricEventBus] = None


def get_event_bus() -> FabricEventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = FabricEventBus()
    return _bus_instance
