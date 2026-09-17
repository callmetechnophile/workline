"""A2A (Agent-to-Agent) interoperability protocol bridge."""

from typing import Any, Dict, Optional
from armourflow.config.settings import PlatformSettings, get_settings


class A2AInteroperabilityBridge:
    """Provides A2A standardized messaging schema for inter-agent communication."""

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.enabled = self.settings.a2a_enabled
        self.endpoint = self.settings.a2a_endpoint

    def format_message(
        self,
        source_agent_id: str,
        target_agent_id: str,
        action: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Format message in A2A envelope specification."""
        return {
            "protocol": "A2A_v1",
            "source_agent_id": source_agent_id,
            "target_agent_id": target_agent_id,
            "action": action,
            "payload": payload,
            "context": context or {},
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.enabled else "DISABLED",
            "protocol": "A2A",
            "endpoint": self.endpoint,
            "enabled": self.enabled,
        }
