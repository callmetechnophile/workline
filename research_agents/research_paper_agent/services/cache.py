"""
Lightweight in-memory deterministic query cache for research provider calls.
"""

import hashlib
import time
from typing import Dict, List, Optional, Tuple
from research_agents.research_paper_agent.config import research_config
from research_agents.research_paper_agent.schemas import RawPaperRecord


class QueryCache:
    """Cache layer preventing redundant network calls for identical queries."""

    def __init__(self, ttl_seconds: Optional[int] = None, enabled: Optional[bool] = None):
        self.ttl_seconds = (
            ttl_seconds if ttl_seconds is not None else research_config.cache_ttl_seconds
        )
        self.enabled = (
            enabled if enabled is not None else research_config.cache_enabled
        )
        self._store: Dict[str, Tuple[float, List[RawPaperRecord]]] = {}

    def _generate_key(self, provider: str, query: str) -> str:
        """Computes SHA256 hash of provider name and normalized query string."""
        normalized_q = " ".join(query.strip().lower().split())
        payload = f"{provider.strip().lower()}::{normalized_q}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, provider: str, query: str) -> Optional[List[RawPaperRecord]]:
        """Retrieves cached results if valid and not expired."""
        if not self.enabled:
            return None

        key = self._generate_key(provider, query)
        entry = self._store.get(key)
        if not entry:
            return None

        timestamp, records = entry
        if time.time() - timestamp > self.ttl_seconds:
            # Expired
            del self._store[key]
            return None

        return records

    def set(self, provider: str, query: str, records: List[RawPaperRecord]) -> None:
        """Stores records under the hashed key."""
        if not self.enabled:
            return
        key = self._generate_key(provider, query)
        self._store[key] = (time.time(), records)

    def clear(self) -> None:
        """Clears all cached entries."""
        self._store.clear()
