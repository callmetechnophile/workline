"""Scrapling acquisition engine for Workline: Throttled, cached, and bounded concurrent fetching."""

import asyncio
import hashlib
import json
from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    from scrapling import AsyncFetcher, Fetcher, Selector
except ImportError:
    AsyncFetcher = None
    Fetcher = None
    Selector = None

try:
    from scrapling.parser import Adaptor
except ImportError:
    Adaptor = None

from backend.workline.scraping.models import RawVendorResult


class ScrapingCache:
    """Simple disk and memory cache for raw HTML and parsed results."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir or (Path.home() / ".workline" / "scrape_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds
        self._memory: Dict[str, Tuple[float, Any]] = {}

    def _get_key(self, url: str, params: Optional[Dict[str, Any]] = None) -> str:
        raw = f"{url}_{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        key = self._get_key(url, params)
        now = datetime.now(timezone.utc).timestamp()

        # Check memory
        if key in self._memory:
            ts, val = self._memory[key]
            if now - ts < self.ttl_seconds:
                return val

        # Check disk
        fpath = self.cache_dir / f"{key}.json"
        if fpath.exists():
            try:
                with open(fpath, "r", encoding="utf-8") as fp:
                    entry = json.load(fp)
                    if now - entry.get("timestamp", 0) < self.ttl_seconds:
                        val = entry.get("data")
                        self._memory[key] = (entry.get("timestamp", now), val)
                        return val
            except Exception:
                pass
        return None

    def set(self, url: str, data: Any, params: Optional[Dict[str, Any]] = None) -> None:
        key = self._get_key(url, params)
        now = datetime.now(timezone.utc).timestamp()
        self._memory[key] = (now, data)

        fpath = self.cache_dir / f"{key}.json"
        try:
            with open(fpath, "w", encoding="utf-8") as fp:
                json.dump({"timestamp": now, "url": url, "data": data}, fp, indent=2)
        except Exception:
            pass


class ScraplingEngine:
    """
    Acquisition engine wrapping Scrapling with rate limiting, bounded concurrency,
    caching, and error handling.
    """

    def __init__(self, max_concurrent: int = 4, delay_seconds: float = 0.5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.delay_seconds = delay_seconds
        self.cache = ScrapingCache()
        self._fetcher = Fetcher() if Fetcher else None

    async def fetch_html(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
        timeout: int = 15,
    ) -> Optional[str]:
        """Fetch raw HTML for a URL using Scrapling with cache and backoff."""
        if use_cache:
            cached = self.cache.get(url, params)
            if cached:
                return cached

        async with self.semaphore:
            await asyncio.sleep(self.delay_seconds)
            for attempt in range(2):
                try:
                    if self._fetcher:
                        response = self._fetcher.get(url, params=params, timeout=timeout)
                        if response and response.status in (200, 304):
                            html = response.text
                            if use_cache:
                                self.cache.set(url, html, params)
                            return html
                    else:
                        import httpx
                        async with httpx.AsyncClient(timeout=timeout) as client:
                            resp = await client.get(url, params=params, headers={"User-Agent": "Workline-Bot/1.0"})
                            if resp.status_code == 200:
                                html = resp.text
                                if use_cache:
                                    self.cache.set(url, html, params)
                                return html
                except Exception:
                    if attempt == 0:
                        await asyncio.sleep(1.0)
                    else:
                        return None
            return None

    def create_adaptor(self, html_content: str) -> Optional[Any]:
        """Wrap HTML string into a Scrapling Selector or Adaptor for CSS/XPath queries."""
        if not html_content:
            return None
        if Selector:
            try:
                return Selector(html_content)
            except Exception:
                pass
        if Adaptor:
            try:
                return Adaptor(html_content)
            except Exception:
                pass
        return None


# Global scraping engine singleton
scraping_engine = ScraplingEngine()
