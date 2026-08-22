"""Procurement and Component Intelligence caching subsystem."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from cli.wline.core.paths import get_config_dir


class ProcurementCache:
    """Multi-tiered disk and memory cache for API and scraped component intelligence."""

    def __init__(self, namespace: str = "procurement", ttl_seconds: int = 86400):
        self.namespace = namespace
        self.ttl_seconds = ttl_seconds
        self.cache_dir = get_config_dir() / "cache" / namespace
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory: Dict[str, Tuple[float, Any]] = {}

    def _make_key(self, primary: str, params: Optional[Dict[str, Any]] = None) -> str:
        payload = f"{primary}_{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def get(self, primary: str, params: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Fetch cached data if fresh."""
        key = self._make_key(primary, params)
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

    def set(self, primary: str, data: Any, params: Optional[Dict[str, Any]] = None) -> None:
        """Store data in memory and disk cache."""
        key = self._make_key(primary, params)
        now = datetime.now(timezone.utc).timestamp()
        self._memory[key] = (now, data)

        fpath = self.cache_dir / f"{key}.json"
        try:
            with open(fpath, "w", encoding="utf-8") as fp:
                json.dump({"timestamp": now, "key": primary, "data": data}, fp, indent=2)
        except Exception:
            pass

    def clear(self) -> None:
        """Flush memory and disk cache."""
        self._memory.clear()
        try:
            for f in self.cache_dir.glob("*.json"):
                f.unlink(missing_ok=True)
        except Exception:
            pass


# Singleton caches
nexar_cache = ProcurementCache(namespace="nexar", ttl_seconds=86400 * 3)
scrapling_cache = ProcurementCache(namespace="scrapling", ttl_seconds=86400 * 2)
datasheet_cache = ProcurementCache(namespace="datasheets", ttl_seconds=86400 * 7)
