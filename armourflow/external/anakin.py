"""Centralized Anakin scraping provider status and client."""

from typing import Any, Dict, Optional
from armourflow.config.settings import PlatformSettings, get_settings


class CentralAnakinClient:
    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.enabled = self.settings.anakin_enabled
        self.endpoint = self.settings.anakin_endpoint

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "DISABLED",
            "provider": "Anakin",
            "enabled": self.enabled,
            "note": "Disabled by policy. Available as optional integration point.",
        }
