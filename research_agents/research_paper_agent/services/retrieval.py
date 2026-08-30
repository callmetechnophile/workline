"""
Paper normalization and PDF availability detection service.
Constructs verified NormalizedPaper instances without data hallucination.
"""

import hashlib
import re
from typing import List, Optional
from research_agents.research_paper_agent.schemas import NormalizedPaper, RawPaperRecord


class PaperNormalizer:
    """Normalizes raw provider candidates and assesses PDF link availability."""

    @staticmethod
    def is_valid_pdf_url(url: Optional[str]) -> bool:
        """Determines if a URL is a syntactically valid PDF locator."""
        if not url or not isinstance(url, str):
            return False
        clean = url.strip().lower()
        if not (clean.startswith("http://") or clean.startswith("https://")):
            return False
        if clean.endswith(".pdf") or "/pdf/" in clean or "format=pdf" in clean or "download=pdf" in clean:
            return True
        # ArXiv or OpenAccess PDF patterns
        if "arxiv.org/abs/" in clean or "arxiv.org/pdf/" in clean:
            return True
        return False

    @staticmethod
    def derive_pdf_url(paper_url: Optional[str], direct_pdf: Optional[str]) -> Optional[str]:
        """Derives verified PDF link if direct_pdf or paper_url supports open access PDF."""
        if direct_pdf and direct_pdf.strip():
            return direct_pdf.strip()
        if paper_url:
            clean = paper_url.strip()
            # ArXiv auto-conversion
            if "arxiv.org/abs/" in clean:
                return clean.replace("/abs/", "/pdf/") + ".pdf"
            if clean.lower().endswith(".pdf"):
                return clean
        return None

    @classmethod
    def normalize(
        cls,
        raw: RawPaperRecord,
        relevance_score: float = 0.0,
        relevance_reasons: Optional[List[str]] = None,
    ) -> NormalizedPaper:
        """Constructs NormalizedPaper instance from RawPaperRecord without fabricating missing data."""
        # Derive stable paper_id
        if raw.paper_id and raw.paper_id.strip():
            paper_id = raw.paper_id.strip()
        elif raw.doi and raw.doi.strip():
            paper_id = f"doi:{raw.doi.strip()}"
        else:
            norm_title = re.sub(r"[^\w]", "", raw.title.lower())
            paper_id = f"paper_{hashlib.md5(norm_title.encode('utf-8')).hexdigest()[:12]}"

        pdf_link = cls.derive_pdf_url(raw.paper_url, raw.pdf_url)
        pdf_available = cls.is_valid_pdf_url(pdf_link)

        return NormalizedPaper(
            paper_id=paper_id,
            title=raw.title.strip(),
            authors=raw.authors,
            abstract=raw.abstract,
            publication_date=raw.publication_date,
            doi=raw.doi,
            venue=raw.venue,
            source="freephdlabor",
            paper_url=raw.paper_url,
            pdf_url=pdf_link,
            pdf_available=pdf_available,
            citation_count=raw.citation_count,
            keywords=raw.keywords,
            relevance_score=relevance_score,
            relevance_reasons=relevance_reasons or [],
        )
