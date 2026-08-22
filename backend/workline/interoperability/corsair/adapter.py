"""Corsair Adapter connecting the Interoperability Gateway with Corsair tools and integrations."""

from typing import Any, Dict, List, Optional
from backend.workline.interoperability.capabilities import AgentCapability
from backend.workline.interoperability.corsair.client import CorsairClient
from backend.workline.interoperability.registry import ExternalAgent


class CorsairAdapter:
    """Adapter mediating gateway requests to Corsair integrations."""

    def __init__(self):
        self.client = CorsairClient()

    async def discover(self) -> List[ExternalAgent]:
        """Discover available Corsair agents."""
        return await self.client.discover()

    async def register_integration(self, agent: ExternalAgent) -> None:
        """Register a new Corsair agent manifest."""
        self.client.registry._integrations[agent.agent_id] = agent

    async def get_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Fetch capabilities of a Corsair agent."""
        return await self.client.get_capabilities(agent_id)

    async def invoke(
        self,
        agent_id: str,
        capability: str,
        payload: Dict[str, Any],
        task_id: str,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Invoke Corsair integration capability."""
        return await self.client.invoke(
            agent_id=agent_id,
            capability=capability,
            payload=payload,
            task_id=task_id,
            timeout=timeout,
        )

    async def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query execution status."""
        return await self.client.get_status(task_id)

    async def cancel(self, task_id: str) -> bool:
        """Cancel in-flight Corsair task."""
        return await self.client.cancel(task_id)
