"""
Authoritative Freephdlabor API provider adapter.
Encapsulates all Freephdlabor-specific search protocols, payload normalization, and error translation.
"""

import time
from typing import Any, Dict, List, Optional
import httpx
from loguru import logger

from research_agents.research_paper_agent.config import research_config
from research_agents.research_paper_agent.providers.base import (
    BasePaperProvider,
    MalformedResponseError,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from research_agents.research_paper_agent.schemas import RawPaperRecord


class FreephdlaborProvider(BasePaperProvider):
    """Adapter for Freephdlabor academic paper search."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.api_key = api_key if api_key is not None else research_config.freephdlabor_api_key
        self.base_url = (base_url or research_config.freephdlabor_base_url).rstrip("/")
        self.timeout = timeout or research_config.timeout_seconds
        self._client = http_client

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "WorkflowGuide-ResearchPaperAgent/1.0",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    async def search(
        self,
        query: str,
        limit: int = 20,
        execution_id: Optional[str] = None,
    ) -> List[RawPaperRecord]:
        """
        Executes a research query against Freephdlabor search endpoint.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        start_time = time.time()
        url = f"{self.base_url}/search/papers"
        headers = self._get_headers()
        params = {"q": clean_query, "limit": min(limit, 50)}

        exec_tag = f"[{execution_id}] " if execution_id else ""
        logger.info(
            f"{exec_tag}[FreephdlaborProvider] Querying provider='freephdlabor' "
            f"query='{clean_query}' limit={params['limit']}"
        )

        try:
            if self._client:
                res = await self._client.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.get(
                        url,
                        params=params,
                        headers=headers,
                    )

            latency = time.time() - start_time

            # Status Code Evaluation
            if res.status_code in (401, 403):
                logger.error(f"{exec_tag}[FreephdlaborProvider] Auth error (HTTP {res.status_code})")
                raise ProviderAuthenticationError(
                    f"Freephdlabor authentication failed (HTTP {res.status_code})."
                )

            if res.status_code == 429:
                logger.warning(f"{exec_tag}[FreephdlaborProvider] Rate limit hit (HTTP 429)")
                raise ProviderRateLimitError(
                    "Freephdlabor rate limit exceeded. Retry later."
                )

            if res.status_code >= 500:
                logger.error(f"{exec_tag}[FreephdlaborProvider] Upstream server error (HTTP {res.status_code})")
                raise ProviderUnavailableError(
                    f"Freephdlabor service unavailable (HTTP {res.status_code})."
                )

            if res.status_code != 200:
                logger.error(f"{exec_tag}[FreephdlaborProvider] Unexpected response (HTTP {res.status_code})")
                raise ProviderUnavailableError(
                    f"Freephdlabor returned unexpected status HTTP {res.status_code}."
                )

            # Parse Payload
            try:
                data = res.json()
            except Exception as e:
                logger.error(f"{exec_tag}[FreephdlaborProvider] Failed to parse JSON response: {e}")
                raise MalformedResponseError("Failed to parse Freephdlabor JSON response.")

            papers = self._parse_records(data)
            logger.info(
                f"{exec_tag}[FreephdlaborProvider] Retrieved {len(papers)} candidate papers "
                f"in {latency:.3f}s"
            )
            return papers

        except httpx.TimeoutException as e:
            logger.error(f"{exec_tag}[FreephdlaborProvider] Request timeout: {e}")
            raise ProviderTimeoutError("Freephdlabor request timed out.")

        except httpx.RequestError as e:
            logger.error(f"{exec_tag}[FreephdlaborProvider] Network connection error: {e}")
            raise ProviderUnavailableError(f"Network error connecting to Freephdlabor: {str(e)}")

    def _parse_records(self, data: Any) -> List[RawPaperRecord]:
        """Maps diverse JSON envelope formats from Freephdlabor into RawPaperRecord models."""
        raw_items: List[Dict[str, Any]] = []

        if isinstance(data, list):
            raw_items = [item for item in data if isinstance(item, dict)]
        elif isinstance(data, dict):
            if "papers" in data and isinstance(data["papers"], list):
                raw_items = data["papers"]
            elif "results" in data and isinstance(data["results"], list):
                raw_items = data["results"]
            elif "data" in data and isinstance(data["data"], list):
                raw_items = data["data"]
            elif "items" in data and isinstance(data["items"], list):
                raw_items = data["items"]
            else:
                raw_items = [data]

        records: List[RawPaperRecord] = []
        for item in raw_items:
            title = (
                item.get("title")
                or item.get("paper_title")
                or item.get("name")
                or ""
            ).strip()

            if not title:
                continue

            authors_raw = item.get("authors") or item.get("author_names") or []
            if isinstance(authors_raw, str):
                authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
            elif isinstance(authors_raw, list):
                authors = [
                    (a.get("name") if isinstance(a, dict) else str(a)).strip()
                    for a in authors_raw
                    if a
                ]
            else:
                authors = []

            abstract = (
                item.get("abstract")
                or item.get("summary")
                or item.get("description")
                or None
            )
            if abstract:
                abstract = str(abstract).strip()

            pub_date = (
                item.get("publication_date")
                or item.get("published_date")
                or item.get("year")
                or item.get("date")
                or None
            )
            if pub_date:
                pub_date = str(pub_date).strip()

            doi = (
                item.get("doi")
                or item.get("digital_object_identifier")
                or None
            )
            if doi:
                doi = str(doi).strip()

            venue = (
                item.get("venue")
                or item.get("journal")
                or item.get("conference")
                or item.get("publisher")
                or None
            )
            if venue:
                venue = str(venue).strip()

            paper_url = (
                item.get("paper_url")
                or item.get("url")
                or item.get("link")
                or item.get("doi_url")
                or None
            )
            if paper_url:
                paper_url = str(paper_url).strip()

            pdf_url = (
                item.get("pdf_url")
                or item.get("pdf_link")
                or item.get("open_access_pdf")
                or None
            )
            if pdf_url:
                pdf_url = str(pdf_url).strip()

            citation_count = None
            if "citation_count" in item and item["citation_count"] is not None:
                try:
                    citation_count = int(item["citation_count"])
                except (ValueError, TypeError):
                    citation_count = None

            keywords_raw = item.get("keywords") or item.get("tags") or []
            if isinstance(keywords_raw, list):
                keywords = [str(k).strip() for k in keywords_raw if str(k).strip()]
            elif isinstance(keywords_raw, str):
                keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
            else:
                keywords = []

            paper_id = str(
                item.get("paper_id")
                or item.get("id")
                or doi
                or title
            ).strip()

            records.append(
                RawPaperRecord(
                    paper_id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    publication_date=pub_date,
                    doi=doi,
                    venue=venue,
                    paper_url=paper_url,
                    pdf_url=pdf_url,
                    citation_count=citation_count,
                    keywords=keywords,
                    raw_metadata=item,
                )
            )

        return records
