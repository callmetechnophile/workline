"""
Anakin deep scraping, crawling, and structured web extraction provider adapter.
Encapsulates scraping JavaScript-rendered pages, documentation crawls, and MCP compatibility.
"""

import time
from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from research_agents.web_research_agent.config import web_research_config
from research_agents.web_research_agent.providers.base import (
    ExtractionError,
    InvalidURLError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    WebResearchProvider,
)
from research_agents.web_research_agent.schemas import RawWebResult


class AnakinProvider(WebResearchProvider):
    """Adapter for Anakin scraping, crawling, and DOM browser extraction."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key if api_key is not None else web_research_config.anakin_api_key
        self.base_url = (base_url or web_research_config.anakin_base_url).rstrip("/")
        self.timeout = timeout or web_research_config.anakin_timeout_seconds
        self._client = http_client

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "WorkflowGuide-WebResearchAgent-Anakin/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search(
        self,
        query: str,
        limit: int = 10,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        """Executes targeted extraction query through Anakin search/retrieval API."""
        clean_query = query.strip()
        if not clean_query:
            return []

        start_time = time.time()
        url = f"{self.base_url}/search"
        payload = {
            "query": clean_query,
            "limit": limit,
            "render_js": True,
        }

        exec_tag = f"[{execution_id}] " if execution_id else ""
        logger.info(f"{exec_tag}[AnakinProvider] Querying provider='anakin' query='{clean_query}'")

        try:
            if self._client:
                res = await self._client.post(
                    url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(
                        url,
                        json=payload,
                        headers=self._get_headers(),
                    )

            latency = time.time() - start_time

            if res.status_code in (401, 403):
                raise ProviderAuthenticationError("anakin", "Anakin API authentication failed.")

            if res.status_code == 429:
                raise ProviderRateLimitError("anakin", "Anakin rate limit exceeded.")

            if res.status_code >= 500:
                raise ProviderUnavailableError("anakin", f"Anakin server error (HTTP {res.status_code}).")

            if res.status_code != 200:
                raise ProviderUnavailableError("anakin", f"Anakin returned status HTTP {res.status_code}.")

            data = res.json()
            items = data.get("items", []) or data.get("results", [])
            results: List[RawWebResult] = []

            for it in items:
                if not isinstance(it, dict):
                    continue
                item_url = it.get("url", "").strip()
                item_title = it.get("title", "").strip()
                if not item_url or not item_title:
                    continue

                results.append(
                    RawWebResult(
                        title=item_title,
                        url=item_url,
                        content=it.get("markdown") or it.get("text") or it.get("content"),
                        snippet=it.get("snippet") or it.get("summary"),
                        published_date=it.get("published_date"),
                        author=it.get("author"),
                        publisher=it.get("publisher"),
                        source_tool="anakin",
                        raw_metadata=it,
                    )
                )

            logger.info(f"{exec_tag}[AnakinProvider] Retrieved {len(results)} items in {latency:.3f}s")
            return results

        except httpx.TimeoutException:
            raise ProviderTimeoutError("anakin", "Anakin search timed out.")
        except httpx.RequestError as e:
            raise ProviderUnavailableError("anakin", f"Network error connecting to Anakin: {str(e)}")

    async def extract(
        self,
        url: str,
        execution_id: Optional[str] = None,
    ) -> Optional[RawWebResult]:
        """Scrapes and parses a single JavaScript-rendered or complex web page."""
        clean_url = url.strip()
        if not clean_url or not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            raise InvalidURLError("anakin", f"Invalid URL: {url}")

        start_time = time.time()
        endpoint = f"{self.base_url}/scrape"
        payload = {
            "url": clean_url,
            "render_js": True,
            "extract_metadata": True,
        }

        exec_tag = f"[{execution_id}] " if execution_id else ""
        logger.info(f"{exec_tag}[AnakinProvider] Scraping URL='{clean_url}'")

        try:
            if self._client:
                res = await self._client.post(
                    endpoint,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(
                        endpoint,
                        json=payload,
                        headers=self._get_headers(),
                    )

            if res.status_code in (401, 403):
                raise ProviderAuthenticationError("anakin", "Anakin credentials invalid.")

            if res.status_code == 429:
                raise ProviderRateLimitError("anakin", "Anakin rate limit reached.")

            if res.status_code != 200:
                raise ExtractionError("anakin", f"Anakin scrape failed with status HTTP {res.status_code}.")

            data = res.json()
            title = data.get("title") or clean_url
            content = data.get("markdown") or data.get("text") or data.get("content")

            return RawWebResult(
                title=title,
                url=clean_url,
                content=content,
                snippet=data.get("description") or (content[:300] if content else None),
                published_date=data.get("published_date"),
                author=data.get("author"),
                publisher=data.get("site_name") or data.get("publisher"),
                source_tool="anakin",
                raw_metadata=data,
            )

        except httpx.TimeoutException:
            raise ProviderTimeoutError("anakin", "Anakin page scrape timed out.")
        except httpx.RequestError as e:
            raise ProviderUnavailableError("anakin", f"Network error during Anakin scrape: {str(e)}")

    async def crawl(
        self,
        url: str,
        max_depth: int = 1,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        """Recursively crawls documentation pages from a starting URL."""
        clean_url = url.strip()
        if not clean_url:
            return []

        endpoint = f"{self.base_url}/crawl"
        payload = {
            "url": clean_url,
            "max_depth": max_depth,
            "max_pages": 5,
        }

        try:
            if self._client:
                res = await self._client.post(
                    endpoint,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout * 2,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout * 2) as client:
                    res = await client.post(
                        endpoint,
                        json=payload,
                        headers=self._get_headers(),
                    )

            if res.status_code == 200:
                data = res.json()
                pages = data.get("pages", [])
                results: List[RawWebResult] = []
                for p in pages:
                    p_url = p.get("url", "").strip()
                    p_title = p.get("title", "").strip()
                    if p_url and p_title:
                        results.append(
                            RawWebResult(
                                title=p_title,
                                url=p_url,
                                content=p.get("markdown") or p.get("text"),
                                snippet=p.get("snippet"),
                                source_tool="anakin",
                                raw_metadata=p,
                            )
                        )
                return results
            return []
        except Exception:
            # Fallback to single page extract if crawl endpoint is not available
            single = await self.extract(url, execution_id=execution_id)
            return [single] if single else []
