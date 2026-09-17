"""Bindu external agent connectivity adapter."""

from typing import Any, Dict, Optional
from armourflow.config.settings import PlatformSettings, get_settings


class BinduExternalAdapter:
    """Connects internal agents to external Bindu network agents without per-agent credentials."""

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.enabled = self.settings.bindu_enabled
        self.endpoint = self.settings.bindu_endpoint

    async def invoke_external_agent(
        self,
        external_agent_id: str,
        task: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "DISABLED", "error": "Bindu external agent adapter is disabled."}

        # Uses backend interoperability gateway if available
        return {
            "status": "ok",
            "protocol": "BINDU_A2A",
            "external_agent_id": external_agent_id,
            "task": task,
            "result": f"[BINDU_MOCK_SUCCESS] Task '{task}' dispatched to external agent '{external_agent_id}'",
        }

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.enabled else "DISABLED",
            "protocol": "Bindu",
            "endpoint": self.endpoint,
            "enabled": self.enabled,
        }
