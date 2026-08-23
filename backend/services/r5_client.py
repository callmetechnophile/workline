"""
Workline R5 Procurement & x402 Service Client for R1 Gateway.
Provides resilient, authenticated async calls to R5 Procurement, Orders & Payment Service.
"""

import os
from typing import Dict, Any, Optional, List
import httpx
from loguru import logger


class R5ProcurementClient:
    """Async HTTP Client for invoking R5 Procurement Service from R1 Gateway."""

    def __init__(self):
        self.base_url = os.getenv("R5_INTERNAL_URL", os.getenv("WORKLINE_R5_URL", "http://localhost:10005")).rstrip("/")
        self.service_token = os.getenv("R5_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))
        self.timeout = float(os.getenv("R5_TIMEOUT_SECONDS", "30.0"))

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

    async def search_components(self, query: str, limit: int = 10, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Searches components via R5."""
        endpoint = f"{self.base_url}/internal/procurement/search"
        headers = self._get_headers(request_id)
        payload = {"query": query, "limit": limit}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R5 Search returned status {response.status_code}")
                return {"query": query, "count": 0, "candidates": [], "error": f"R5 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R5 Search connection error: {e}")
            return {"query": query, "count": 0, "candidates": [], "error": "R5 service unavailable"}

    async def create_order_plan(self, project_id: str, bom_id: str, user_id: str = "user:engineer", team_id: str = "team:default", request_id: Optional[str] = None) -> Dict[str, Any]:
        """Creates an order plan via R5."""
        endpoint = f"{self.base_url}/internal/procurement/orders/plan"
        headers = self._get_headers(request_id)
        payload = {"project_id": project_id, "bom_id": bom_id, "user_id": user_id, "team_id": team_id}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R5 Order Plan returned status {response.status_code}")
                return {"error": f"R5 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R5 Order Plan connection error: {e}")
            return {"error": "R5 service unavailable"}

    async def request_x402_payment(self, order_id: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Requests x402 payment challenge via R5."""
        endpoint = f"{self.base_url}/internal/procurement/payments/request"
        headers = self._get_headers(request_id)
        payload = {"order_id": order_id}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R5 Payment request returned status {response.status_code}")
                return {"error": f"R5 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R5 Payment request connection error: {e}")
            return {"error": "R5 service unavailable"}


r5_client = R5ProcurementClient()
