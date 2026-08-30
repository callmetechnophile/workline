"""
Lightweight in-memory deterministic query and URL cache for web research calls.
"""

import hashlib
import time
from typing import Dict, List, Optional, Tuple
from research_agents.web_research_agent.config import web_research_config
from research_agents.web_research_agent.schemas import RawWebResult


class WebQueryCache:
    """Cache layer preventing redundant network calls for identical queries or URLs."""

    def __init__(self, ttl_seconds: Optional[int] = None, enabled: Optional[bool] = None):
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else web_research_config.cache_ttl_seconds
        )
        self.enabled = (
            enabled if enabled is not None else web_research_config.cache_enabled
        )
        self._store: Dict[str, Tuple[float, List[RawWebResult]]] = {}

    def _generate_key(self, provider: str, target: str) -> str:
        """Computes SHA256 hash of provider name and normalized target string."""
        normalized = " ".join(target.strip().lower().split())
        payload = f"{provider.strip().lower()}::{normalized}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, provider: str, target: str) -> Optional[List[RawWebResult]]:
        """Retrieves cached results if valid and not expired."""
        if not self.enabled:
            return None

        key = self._generate_key(provider, target)
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, records = entry
        if time.time() - timestamp > self.ttl_seconds:
            del self._store[key]
            return None

        return records

    def set(self, provider: str, target: str, records: List[RawWebResult]) -> None:
        """Stores records under the hashed key."""
        if not self.enabled:
            return
        key = self._generate_key(provider, target)
        self._store[key] = (time.time(), records)

    def clear(self) -> None:
        """Clears all cached entries."""
        self._store.clear()
