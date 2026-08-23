"""
Workline R4 Engineering Service Client for R1 Gateway.
Provides resilient, authenticated async calls to R4 Engineering & Simulation Service.
"""

import os
from typing import Dict, Any, Optional, List
import httpx
from loguru import logger


class R4EngineeringClient:
    """Async HTTP Client for invoking R4 Engineering Service from R1 Gateway."""

    def __init__(self):
        self.base_url = os.getenv("R4_INTERNAL_URL", os.getenv("WORKLINE_R4_URL", "http://localhost:10004")).rstrip("/")
        self.service_token = os.getenv("R4_SERVICE_TOKEN", os.getenv("WORKLINE_SERVICE_AUTH_KEY", ""))
        self.timeout = float(os.getenv("R4_TIMEOUT_SECONDS", "30.0"))

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

    async def convert_units(self, value: float, from_unit: str, to_unit: str, unit_type: Optional[str] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Converts units via R4."""
        endpoint = f"{self.base_url}/internal/engineering/units/convert"
        headers = self._get_headers(request_id)
        payload = {"value": value, "from_unit": from_unit, "to_unit": to_unit, "unit_type": unit_type}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R4 Unit conversion returned status {response.status_code}")
                return {"success": False, "error": f"R4 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R4 Unit conversion connection error: {e}")
            return {"success": False, "error": "R4 service unavailable"}

    async def validate_requirement(self, requirement_id: str, candidate_component_id: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Evaluates requirements candidate via R4."""
        endpoint = f"{self.base_url}/internal/engineering/requirements/validate"
        headers = self._get_headers(request_id)
        payload = {"requirement_id": requirement_id, "candidate_component_id": candidate_component_id}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R4 Requirement validation returned status {response.status_code}")
                return {"valid": False, "error": f"R4 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R4 Requirement validation connection error: {e}")
            return {"valid": False, "error": "R4 service unavailable"}

    async def predict_pinn_thermal(self, project_dict: Dict[str, Any], nx: int = 50, ny: int = 40, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Runs PINN thermal surrogate via R4."""
        endpoint = f"{self.base_url}/internal/engineering/pinn/thermal"
        headers = self._get_headers(request_id)
        payload = {"project_dict": project_dict, "nx": nx, "ny": ny}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(endpoint, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"R4 PINN thermal returned status {response.status_code}")
                return {"error": f"R4 returned {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"R4 PINN thermal connection error: {e}")
            return {"error": "R4 service unavailable"}


r4_client = R4EngineeringClient()
