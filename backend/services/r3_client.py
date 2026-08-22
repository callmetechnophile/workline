"""
Workline R3 Knowledge Service Client for R1 Gateway.
Provides resilient, authenticated async calls to R3 Knowledge Infrastructure.
"""

import os
from typing import Dict, Any, Optional, List
import httpx
from loguru import logger


class R3KnowledgeClient:
    """Async HTTP Client for invoking R3 Knowledge Service from R1 Gateway."""

    def __init__(self):
        self.base_url = os.getenv("R3_INTERNAL_URL", os.getenv("WORKLINE_R3_URL", "http://localhost:10003")).rstrip("/")
        self.service_token = os.getenv("R3_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))
        self.timeout = float(os.getenv("R3_TIMEOUT_SECONDS", "15.0"))

    def _get_headers(self, request_id: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
            headers["X-Workline-Service-Token"] = self.service_token
        if request_id:
            headers["X-Request-ID"] = request_id
        return headers

    async def search(self, query: str, limit: int = 10, collection: str = "components", request_id: Optional[str] = None) -> Dict[str, Any]:
        """Performs vector search through R3."""
        endpoint = f"{self.base_url}/internal/knowledge/search"
        headers = self._get_headers(request_id)
        payload = {"query": query, "limit": limit, "collection": collection}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R3 Knowledge search returned status {response.status_code}")
                return {"query": query, "results": [], "status": "degraded"}
        except httpx.RequestError as e:
            logger.error(f"R3 Knowledge search connection error: {e}")
            return {"query": query, "results": [], "status": "unavailable"}

    async def query_graph(self, query: str, params: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes graph traversal through R3."""
        endpoint = f"{self.base_url}/internal/graph/query"
        headers = self._get_headers(request_id)
        payload = {"query": query, "params": params or {}}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R3 Graph query returned status {response.status_code}")
                return {"query": query, "result": [], "status": "degraded"}
        except httpx.RequestError as e:
            logger.error(f"R3 Graph query connection error: {e}")
            return {"query": query, "result": [], "status": "unavailable"}


r3_client = R3KnowledgeClient()
