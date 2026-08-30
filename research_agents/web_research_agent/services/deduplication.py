"""
Deterministic web source deduplication service for WebResearchAgent.
Deduplicates candidate sources based on canonical URL, tracking parameter stripping,
domain + normalized title, and content fingerprints.
"""

import hashlib
import re
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from typing import List, Set
from research_agents.web_research_agent.schemas import RawWebResult


class WebSourceDeduplicator:
    """Deduplicates raw web search results using strict hierarchical matching."""

    TRACKING_PARAMS = {
        "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
        "ref", "fbclid", "gclid", "source", "ref_src", "feature"
    }

    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalizes URL by stripping tracking parameters, fragments, protocol differences,
        and trailing slashes.
        """
        if not url:
            return ""
        parsed = urlparse(url.strip())
        scheme = "https"  # Canonicalize to https
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path.rstrip("/")

        # Filter out tracking query parameters
        query_params = parse_qs(parsed.query, keep_blank_values=False)
        filtered_params = {
            k: v for k, v in query_params.items()
            if k.lower() not in cls.TRACKING_PARAMS
        }
        clean_query = urlencode(filtered_params, doseq=True)

        return urlunparse((scheme, netloc, path, "", clean_query, ""))

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalizes title string."""
        clean = re.sub(r"[^\w\s]", " ", title.lower())
        return " ".join(clean.split())

    @staticmethod
    def compute_content_fingerprint(content: str) -> str:
        """Computes SHA-256 fingerprint for non-empty text content."""
        if not content or len(content.strip()) < 50:
            return ""
        tokens = [w for w in re.sub(r"[^\w\s]", "", content.lower()).split() if len(w) > 3]
        sample = " ".join(tokens[:100])
        return hashlib.sha256(sample.encode("utf-8")).hexdigest()

    def deduplicate(self, results: List[RawWebResult]) -> List[RawWebResult]:
        """
        Deduplicates candidate results in order:
        1. Canonical normalized URL
        2. Domain + normalized title
        3. Content fingerprint
        """
        unique_results: List[RawWebResult] = []
        seen_urls: Set[str] = set()
        seen_domain_titles: Set[str] = set()
        seen_fingerprints: Set[str] = set()

        for res in results:
            norm_url = self.normalize_url(res.url)
            if not norm_url or norm_url in seen_urls:
                continue

            parsed = urlparse(norm_url)
            domain = parsed.netloc
            norm_title = self.normalize_title(res.title)
            domain_title_key = f"{domain}::{norm_title}"
            if norm_title and domain_title_key in seen_domain_titles:
                continue

            fingerprint = self.compute_content_fingerprint(res.content or res.snippet or "")
            if fingerprint and fingerprint in seen_fingerprints:
                continue

            seen_urls.add(norm_url)
            if norm_title:
                seen_domain_titles.add(domain_title_key)
            if fingerprint:
                seen_fingerprints.add(fingerprint)

            # Update URL to clean canonical form
            res.url = norm_url
            unique_results.append(res)

        return unique_results
