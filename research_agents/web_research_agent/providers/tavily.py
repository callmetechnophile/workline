"""
Tavily web search and retrieval provider adapter.
Encapsulates all Tavily-specific API calls, authentication, payload mapping, and error translation.
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


class TavilyProvider(WebResearchProvider):
    """Adapter for Tavily search and content retrieval."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key if api_key is not None else web_research_config.tavily_api_key
        self.base_url = (base_url or web_research_config.tavily_base_url).rstrip("/")
        self.timeout = timeout or web_research_config.tavily_timeout_seconds
        self._client = http_client

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "WorkflowGuide-WebResearchAgent/1.0",
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
        """Executes a web search query through Tavily API."""
        clean_query = query.strip()
        if not clean_query:
            return []

        start_time = time.time()
        url = f"{self.base_url}/search"
        payload = {
            "api_key": self.api_key,
            "query": clean_query,
            "search_depth": "advanced",
            "max_results": min(limit, 20),
            "include_answer": False,
            "include_raw_content": False,
        }

        exec_tag = f"[{execution_id}] " if execution_id else ""
        logger.info(
            f"{exec_tag}[TavilyProvider] Searching provider='tavily' "
            f"query='{clean_query}' limit={payload['max_results']}"
        )

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
                logger.error(f"{exec_tag}[TavilyProvider] Authentication failure (HTTP {res.status_code})")
                raise ProviderAuthenticationError("tavily", "Tavily API key is invalid or unauthorized.")

            if res.status_code == 429:
                logger.warning(f"{exec_tag}[TavilyProvider] Rate limit hit (HTTP 429)")
                raise ProviderRateLimitError("tavily", "Tavily rate limit exceeded.")

            if res.status_code >= 500:
                logger.error(f"{exec_tag}[TavilyProvider] Server error (HTTP {res.status_code})")
                raise ProviderUnavailableError("tavily", f"Tavily service error (HTTP {res.status_code}).")

            if res.status_code != 200:
                logger.error(f"{exec_tag}[TavilyProvider] Unexpected status (HTTP {res.status_code})")
                raise ProviderUnavailableError("tavily", f"Tavily returned unexpected status {res.status_code}.")

            data = res.json()
            results_raw = data.get("results", [])
            parsed_results: List[RawWebResult] = []

            for item in results_raw:
                if not isinstance(item, dict):
                    continue
                item_url = item.get("url", "").strip()
                item_title = item.get("title", "").strip()
                if not item_url or not item_title:
                    continue

                parsed_results.append(
                    RawWebResult(
                        title=item_title,
                        url=item_url,
                        content=item.get("content"),
                        snippet=item.get("snippet") or item.get("content"),
                        published_date=item.get("published_date"),
                        author=item.get("author"),
                        publisher=item.get("publisher"),
                        source_tool="tavily",
                        raw_metadata=item,
                    )
                )

            logger.info(
                f"{exec_tag}[TavilyProvider] Retrieved {len(parsed_results)} sources in {latency:.3f}s"
            )
            return parsed_results

        except httpx.TimeoutException as e:
            logger.error(f"{exec_tag}[TavilyProvider] Request timeout: {e}")
            raise ProviderTimeoutError("tavily", "Tavily search request timed out.")

        except httpx.RequestError as e:
            logger.error(f"{exec_tag}[TavilyProvider] Network connection error: {e}")
            raise ProviderUnavailableError("tavily", f"Network error connecting to Tavily: {str(e)}")

    async def extract(
        self,
        url: str,
        execution_id: Optional[str] = None,
    ) -> Optional[RawWebResult]:
        """Extracts content from a single URL via Tavily extract endpoint."""
        clean_url = url.strip()
        if not clean_url or not (clean_url.startswith("http://") or clean_url.startswith("https://")):
            raise InvalidURLError("tavily", f"Invalid URL: {url}")

        extract_url = f"{self.base_url}/extract"
        payload = {
            "api_key": self.api_key,
            "urls": [clean_url],
        }

        try:
            if self._client:
                res = await self._client.post(
                    extract_url,
                    json=payload,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.post(
                        extract_url,
                        json=payload,
                        headers=self._get_headers(),
                    )

            if res.status_code == 200:
                data = res.json()
                results = data.get("results", [])
                if results and isinstance(results[0], dict):
                    item = results[0]
                    return RawWebResult(
                        title=item.get("title") or clean_url,
                        url=clean_url,
                        content=item.get("raw_content") or item.get("content"),
                        snippet=item.get("snippet"),
                        source_tool="tavily",
                        raw_metadata=item,
                    )
            return None
        except Exception as e:
            raise ExtractionError("tavily", f"Tavily failed to extract URL '{clean_url}': {str(e)}")

    async def crawl(
        self,
        url: str,
        max_depth: int = 1,
        execution_id: Optional[str] = None,
    ) -> List[RawWebResult]:
        """Fallback crawl delegating single extraction on base URL."""
        res = await self.extract(url, execution_id=execution_id)
        return [res] if res else []
