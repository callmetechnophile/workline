"""
Deterministic paper deduplication service.
Deduplicates candidate papers based on DOI, normalized title, source ID, and URLs.
"""

import re
from typing import List, Set
from research_agents.research_paper_agent.schemas import RawPaperRecord


class PaperDeduplicator:
    """Deduplicates raw research paper records using strict hierarchical matching."""

    @staticmethod
    def normalize_doi(doi: str) -> str:
        """Normalizes DOI by lowercasing and stripping prefix resolvers."""
        clean = doi.strip().lower()
        clean = re.sub(r"^https?://(dx\.)?doi\.org/", "", clean)
        return clean.strip()

    @staticmethod
    def normalize_title(title: str) -> str:
        """Normalizes titles by lowercasing, converting punctuation/hyphens to spaces, and collapsing whitespace."""
        clean = title.lower()
        clean = re.sub(r"[^\w\s]", " ", clean)
        words = clean.split()
        return " ".join(words)


    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalizes URL for canonical comparison."""
        clean = url.strip().lower()
        clean = re.sub(r"^https?://(www\.)?", "", clean)
        clean = clean.rstrip("/")
        return clean

    def deduplicate(self, records: List[RawPaperRecord]) -> List[RawPaperRecord]:
        """
        Deduplicates candidate records in priority order:
        1. DOI
        2. Normalized title
        3. Source paper ID
        4. Canonical paper URL
        """
        unique_records: List[RawPaperRecord] = []
        seen_dois: Set[str] = set()
        seen_titles: Set[str] = set()
        seen_ids: Set[str] = set()
        seen_urls: Set[str] = set()

        for rec in records:
            # 1. DOI Matching
            if rec.doi:
                norm_doi = self.normalize_doi(rec.doi)
                if norm_doi:
                    if norm_doi in seen_dois:
                        continue
                    seen_dois.add(norm_doi)

            # 2. Normalized Title Matching
            norm_title = self.normalize_title(rec.title)
            if norm_title:
                if norm_title in seen_titles:
                    continue
                seen_titles.add(norm_title)

            # 3. Source Paper ID Matching
            if rec.paper_id:
                norm_id = rec.paper_id.strip().lower()
                if norm_id:
                    if norm_id in seen_ids:
                        continue
                    seen_ids.add(norm_id)

            # 4. Canonical URL Matching
            if rec.paper_url:
                norm_url = self.normalize_url(rec.paper_url)
                if norm_url:
                    if norm_url in seen_urls:
                        continue
                    seen_urls.add(norm_url)

            unique_records.append(rec)

        return unique_records
