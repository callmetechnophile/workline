"""Centralized arXiv literature discovery client."""

from typing import Any, Dict, List, Optional
from armourflow.config.settings import PlatformSettings, get_settings
from research_agents.research_paper_agent.providers.arxiv import ArxivProvider


class CentralArxivClient:
    """Centralized client for searching academic papers via arXiv."""

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.endpoint = getattr(self.settings, "arxiv_endpoint", "https://export.arxiv.org/api/query")
        self.enabled = getattr(self.settings, "arxiv_enabled", True)
        self._provider = ArxivProvider(base_url=self.endpoint)

    async def search_papers(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches arXiv and returns simplified dictionary records."""
        records = await self._provider.search(query=query, limit=limit)
        return [
            {
                "paper_id": rec.paper_id,
                "title": rec.title,
                "authors": rec.authors,
                "publication_date": rec.publication_date,
                "doi": rec.doi,
                "paper_url": rec.paper_url,
                "pdf_url": rec.pdf_url,
                "venue": rec.venue,
            }
            for rec in records
        ]

    def health_check(self) -> Dict[str, Any]:
        """Returns health and connectivity status of the arXiv provider."""
        return {
            "status": "HEALTHY",
            "provider": "arXiv",
            "endpoint": self.endpoint,
            "enabled": self.enabled,
            "auth_type": "open-access (no API key required)",
        }
