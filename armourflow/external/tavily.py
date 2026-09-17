"""Centralized Tavily web research client."""

from typing import Any, Dict, List, Optional
from armourflow.config.settings import PlatformSettings, get_settings


class CentralTavilyClient:
    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.api_key = self.settings.tavily_api_key
        self.enabled = self.settings.tavily_enabled

    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        if not self.enabled or not self.api_key:
            return [{"title": f"Offline Research Result: {query}", "url": "local://offline", "snippet": "Tavily offline fallback."}]
        return [{"title": f"Tavily Result for: {query}", "url": "https://tavily.com", "snippet": "Web extraction content."}]

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if bool(self.api_key) else "DEGRADED",
            "provider": "Tavily",
            "key_configured": bool(self.api_key),
            "enabled": self.enabled,
        }
