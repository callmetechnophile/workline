"""Bindu A2A Adapter connecting the Interoperability Gateway with Bindu network clients."""

from typing import Any, Dict, List, Optional
from backend.workline.interoperability.bindu.client import BinduClient
from backend.workline.interoperability.bindu.discovery import BinduDiscoveryService
from backend.workline.interoperability.bindu.server import BinduServer
from backend.workline.interoperability.capabilities import AgentCapability
from backend.workline.interoperability.registry import ExternalAgent


class BinduAdapter:
    """Adapter for mediating communication between Workline Interoperability Gateway and Bindu network."""

    def __init__(self):
        self.client = BinduClient()
        self.server = BinduServer()

    async def discover(self) -> List[ExternalAgent]:
        """Discover agents operating on the Bindu protocol."""
        return BinduDiscoveryService.probe_agent_network()

    async def get_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Fetch capabilities of a specific Bindu agent."""
        return await self.client.get_capabilities(agent_id)

    async def execute(
        self,
        agent_id: str,
        capability: str,
        payload: Dict[str, Any],
        task_id: str,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Dispatch task to Bindu agent."""
        return await self.client.send_task(
            agent_id=agent_id,
            capability=capability,
            payload=payload,
            task_id=task_id,
            timeout=timeout,
        )

    async def get_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve task execution status."""
        return await self.client.get_task_status(task_id)

    async def cancel(self, task_id: str) -> bool:
        """Cancel a running task on Bindu network."""
        return await self.client.cancel_task(task_id)
