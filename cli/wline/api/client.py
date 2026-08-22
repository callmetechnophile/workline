"""Workline SDK boundary client for connecting the CLI to the backend server."""

import os
from typing import Any, Dict, Optional
import httpx


class WorklineClient:
    """
    Client for interacting with the Workline backend API.
    Acts as the SDK boundary between CLI commands and backend services.
    """

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or os.environ.get("WORKLINE_API_URL", "http://localhost:8000")).rstrip("/")
        self.timeout = 15.0

    def health_check(self) -> bool:
        """Check if the backend server is reachable."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/openapi.json")
                return res.status_code == 200
        except Exception:
            return False

    def get_version(self) -> Dict[str, Any]:
        """Fetch server version metadata."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.get(f"{self.base_url}/openapi.json")
                if res.status_code == 200:
                    info = res.json().get("info", {})
                    return {"version": info.get("version", "0.1.0"), "title": info.get("title", "Workline")}
        except Exception:
            pass
        return {"version": "0.1.0", "title": "Workline"}
