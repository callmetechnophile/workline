"""
Amazon EventBridge domain event emitter for Workline / ArmourFlow platform.
Dispatches canonical lifecycle events to an EventBridge Custom EventBus.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional
from loguru import logger


class EventBridgePublisher:
    """
    Publishes domain events to AWS EventBridge.
    Falls back to local logging and callback handlers if AWS is unavailable.
    """

    def __init__(
        self,
        event_bus_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
    ):
        self.event_bus_name = event_bus_name or os.environ.get("EVENTBRIDGE_BUS_NAME", "workline-events")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.endpoint_url = endpoint_url or os.environ.get("EVENTBRIDGE_ENDPOINT_URL")
        self._client = None
        self._published_events: List[Dict[str, Any]] = []
        self._init_client()

    def _init_client(self):
        try:
            import boto3
            kwargs: Dict[str, Any] = {"region_name": self.region_name}
            if self.endpoint_url:
                kwargs["endpoint_url"] = self.endpoint_url
            self._client = boto3.client("events", **kwargs)
            logger.info(f"[EventBridge] Initialized client for bus '{self.event_bus_name}'")
        except Exception as e:
            logger.warning(f"[EventBridge] Could not initialize client ({e}); using local event tracking.")
            self._client = None

    async def publish_event(
        self,
        detail_type: str,
        detail: Dict[str, Any],
        source: str = "workline.platform",
        resources: Optional[List[str]] = None,
    ) -> bool:
        """
        Publish a structured event to EventBridge.
        detail_type examples:
          - 'ProjectCreated'
          - 'ResearchStarted'
          - 'ResearchCompleted'
          - 'BOMGenerated'
          - 'BOMOptimized'
          - 'ValidationFailed'
          - 'ReportGenerated'
          - 'AgentDelegated'
          - 'PolicyViolation'
        """
        entry = {
            "Time": time.time(),
            "Source": source,
            "DetailType": detail_type,
            "Detail": json.dumps(detail),
            "EventBusName": self.event_bus_name,
        }
        if resources:
            entry["Resources"] = resources

        self._published_events.append({
            "detail_type": detail_type,
            "detail": detail,
            "source": source,
            "timestamp": time.time(),
        })

        if not self._client:
            logger.debug(f"[EventBridge Local] Event {detail_type} logged.")
            return True

        try:
            resp = self._client.put_events(Entries=[entry])
            failed_count = resp.get("FailedEntryCount", 0)
            if failed_count > 0:
                logger.warning(f"[EventBridge] Failed to deliver event: {resp.get('Entries')}")
                return True
            return True
        except Exception as e:
            logger.warning(f"[EventBridge] put_events failed ({e}); recorded in local event buffer.")
            return True

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent events from local buffer for testing."""
        return self._published_events[-limit:]


# Global singleton instance
event_publisher = EventBridgePublisher()
