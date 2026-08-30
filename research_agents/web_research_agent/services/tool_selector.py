"""
Deterministic tool selection policy for WebResearchAgent.
Directs tasks to Tavily (search/discovery) or Anakin (deep scraping/crawling/DOM),
and detects academic queries for Agent #1 delegation.
"""

from typing import List, Literal, Optional, Tuple


ToolChoice = Literal["tavily_search", "tavily_extract", "anakin_scrape", "anakin_crawl", "delegate_academic"]


class ToolSelector:
    """Evaluates task intent and selects optimal tool according to policy."""

    ACADEMIC_KEYWORDS = {
        "arxiv", "ieee xplore", "pubmed", "doi", "peer reviewed", "journal paper",
        "conference proceedings", "freephdlabor", "springer link", "acm digital library"
    }

    JS_HEAVY_OR_SCRAPE_DOMAINS = {
        "digikey.com", "mouser.com", "ti.com", "st.com", "analog.com",
        "espressif.com", "nxp.com", "microchip.com", "adafruit.com", "sparkfun.com"
    }

    def select_tool(
        self,
        task_intent: str,
        target_url: Optional[str] = None,
        query: Optional[str] = None,
    ) -> Tuple[ToolChoice, str]:
        """
        Determines the appropriate tool and provides deterministic reasoning.

        Returns:
            (ToolChoice, reason_string)
        """
        intent = task_intent.lower()
        combined_text = f"{intent} {query or ''} {target_url or ''}".lower()

        # 1. Academic Paper Query Check -> Agent #1 Routing
        for ak in self.ACADEMIC_KEYWORDS:
            if ak in combined_text:
                return (
                    "delegate_academic",
                    f"Task involves academic paper discovery ('{ak}'). Route to Agent #1 (ResearchPaperAgent / Freephdlabor).",
                )

        # 2. Known URL Extraction / Scrape
        if target_url:
            if "crawl" in intent or "docs" in target_url or "documentation" in target_url:
                return (
                    "anakin_crawl",
                    "Task targets multi-page documentation crawl via Anakin.",
                )
            if any(dom in target_url.lower() for dom in self.JS_HEAVY_OR_SCRAPE_DOMAINS) or "js" in intent:
                return (
                    "anakin_scrape",
                    "Target is a vendor or JS-rendered page requiring Anakin browser-based extraction.",
                )
            return (
                "anakin_scrape",
                "Extracting structured content from a designated URL via Anakin.",
            )

        # 3. Broad Web Search / Discovery
        if "find sources" in intent or "search" in intent or "github" in intent:
            return (
                "tavily_search",
                "Broad web discovery and candidate finding via Tavily search.",
            )

        if "vendor" in intent or "datasheet" in intent or "pricing" in intent:
            return (
                "tavily_search",
                "Searching component datasheets and manufacturer documents via Tavily.",
            )

        # Default fallback
        return (
            "tavily_search",
            "General web engineering investigation via Tavily search.",
        )
