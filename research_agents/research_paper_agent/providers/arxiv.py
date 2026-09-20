"""
Authoritative arXiv API provider adapter.
Encapsulates arXiv-specific Atom XML search protocols, payload normalization, and error translation.
"""

import time
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import httpx
from loguru import logger

from research_agents.research_paper_agent.config import research_config
from research_agents.research_paper_agent.providers.base import (
    BasePaperProvider,
    MalformedResponseError,
    ProviderRateLimitError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)
from research_agents.research_paper_agent.schemas import RawPaperRecord

# Atom XML namespaces used by arXiv API
ATOM_NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


class ArxivProvider(BasePaperProvider):
    """Adapter for arXiv academic paper search via Atom XML feed."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        self.base_url = (base_url or research_config.arxiv_base_url).rstrip("/")
        self.timeout = timeout or research_config.timeout_seconds
        self._client = http_client

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/atom+xml, application/xml, text/xml",
            "User-Agent": "WorkflowGuide-ResearchPaperAgent/1.0 (academic-research-bot)",
        }

    async def search(
        self,
        query: str,
        limit: int = 20,
        execution_id: Optional[str] = None,
    ) -> List[RawPaperRecord]:
        """
        Executes an academic research query against the arXiv Atom query API.
        """
        clean_query = query.strip()
        if not clean_query:
            return []

        # Target title, abstract, and full-text fields via 'all:' search syntax
        search_query = f"all:{clean_query}"
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": min(max(limit, 1), 50),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }

        exec_tag = f"[{execution_id}] " if execution_id else ""
        logger.info(
            f"{exec_tag}[ArxivProvider] Querying provider='arxiv' "
            f"query='{clean_query}' limit={params['max_results']}"
        )

        start_time = time.time()
        try:
            if self._client:
                res = await self._client.get(
                    self.base_url,
                    params=params,
                    headers=self._get_headers(),
                    timeout=self.timeout,
                )
            else:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    res = await client.get(
                        self.base_url,
                        params=params,
                        headers=self._get_headers(),
                    )

            latency = time.time() - start_time

            if res.status_code == 429:
                logger.warning(f"{exec_tag}[ArxivProvider] Rate limit hit (HTTP 429)")
                raise ProviderRateLimitError("arXiv rate limit exceeded. Retry later.")

            if res.status_code >= 500:
                logger.error(f"{exec_tag}[ArxivProvider] Upstream server error (HTTP {res.status_code})")
                raise ProviderUnavailableError(f"arXiv service unavailable (HTTP {res.status_code}).")

            if res.status_code != 200:
                logger.error(f"{exec_tag}[ArxivProvider] Unexpected status HTTP {res.status_code}")
                raise ProviderUnavailableError(f"arXiv returned unexpected status HTTP {res.status_code}.")

            papers = self._parse_atom_feed(res.text)
            logger.info(
                f"{exec_tag}[ArxivProvider] Retrieved {len(papers)} candidate papers in {latency:.3f}s"
            )
            return papers

        except httpx.TimeoutException as e:
            logger.error(f"{exec_tag}[ArxivProvider] Request timeout: {e}")
            raise ProviderTimeoutError("arXiv search request timed out.")

        except httpx.RequestError as e:
            logger.error(f"{exec_tag}[ArxivProvider] Network error: {e}")
            raise ProviderUnavailableError(f"Network error connecting to arXiv: {str(e)}")

    def _parse_atom_feed(self, xml_text: str) -> List[RawPaperRecord]:
        """Maps arXiv Atom XML feed into RawPaperRecord models."""
        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            raise MalformedResponseError(f"Failed to parse arXiv Atom XML response: {e}")

        records: List[RawPaperRecord] = []
        entries = root.findall("atom:entry", ATOM_NAMESPACES)

        for entry in entries:
            # Title
            title_el = entry.find("atom:title", ATOM_NAMESPACES)
            if title_el is None or not title_el.text:
                continue
            title = " ".join(title_el.text.split())
            if not title:
                continue

            # Paper ID / URL
            id_el = entry.find("atom:id", ATOM_NAMESPACES)
            paper_url = id_el.text.strip() if id_el is not None and id_el.text else None
            paper_id = paper_url.split("/abs/")[-1] if paper_url and "/abs/" in paper_url else paper_url

            # Abstract / Summary
            summary_el = entry.find("atom:summary", ATOM_NAMESPACES)
            abstract = " ".join(summary_el.text.split()) if summary_el is not None and summary_el.text else None

            # Authors
            authors: List[str] = []
            for author_el in entry.findall("atom:author", ATOM_NAMESPACES):
                name_el = author_el.find("atom:name", ATOM_NAMESPACES)
                if name_el is not None and name_el.text:
                    authors.append(name_el.text.strip())

            # Publication Date
            published_el = entry.find("atom:published", ATOM_NAMESPACES)
            pub_date = published_el.text.strip() if published_el is not None and published_el.text else None

            # PDF and Web Links
            pdf_url = None
            for link in entry.findall("atom:link", ATOM_NAMESPACES):
                rel = link.attrib.get("rel")
                title_attr = link.attrib.get("title")
                href = link.attrib.get("href")
                if title_attr == "pdf" or (rel == "related" and href and "pdf" in href):
                    pdf_url = href
                elif rel == "alternate" and href and not paper_url:
                    paper_url = href

            # Fallback if pdf_url wasn't explicitly tagged
            if not pdf_url and paper_url and "/abs/" in paper_url:
                pdf_url = paper_url.replace("/abs/", "/pdf/") + ".pdf"

            # DOI (if available from journal publication)
            doi_el = entry.find("arxiv:doi", ATOM_NAMESPACES)
            doi = doi_el.text.strip() if doi_el is not None and doi_el.text else None

            # Primary Category / Keywords
            keywords: List[str] = []
            for cat in entry.findall("atom:category", ATOM_NAMESPACES):
                term = cat.attrib.get("term")
                if term:
                    keywords.append(term)

            records.append(
                RawPaperRecord(
                    paper_id=paper_id,
                    title=title,
                    authors=authors,
                    abstract=abstract,
                    publication_date=pub_date,
                    doi=doi,
                    venue="arXiv",
                    paper_url=paper_url,
                    pdf_url=pdf_url,
                    citation_count=None,
                    keywords=keywords,
                    raw_metadata={"source": "arxiv", "id": paper_id},
                )
            )

        return records
