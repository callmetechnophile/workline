"""Bindu A2A client implementation."""

import asyncio
from typing import Any, Dict, List, Optional
from backend.workline.interoperability.bindu.messaging import BinduMessageEnvelope
from backend.workline.interoperability.capabilities import AgentCapability
from backend.workline.interoperability.registry import ExternalAgent, agent_registry


class BinduClient:
    """Client for dispatching and managing tasks via the Bindu Agent-to-Agent (A2A) protocol."""

    def __init__(self, client_id: str = "workline-root-gateway"):
        self.client_id = client_id
        self._active_tasks: Dict[str, Dict[str, Any]] = {}

    async def discover_agent(self, agent_id: str) -> Optional[ExternalAgent]:
        """Discover and fetch manifest for a Bindu agent."""
        agent = agent_registry.get_agent(agent_id)
        if agent and agent.protocol == "BINDU_A2A":
            return agent
        return None

    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve detailed metadata about a Bindu agent."""
        agent = await self.discover_agent(agent_id)
        return agent.model_dump() if agent else None

    async def get_capabilities(self, agent_id: str) -> List[AgentCapability]:
        """Fetch all declared capabilities for a Bindu agent."""
        agent = await self.discover_agent(agent_id)
        return agent.capabilities if agent else []

    async def send_task(
        self,
        agent_id: str,
        capability: str,
        payload: Dict[str, Any],
        task_id: str,
        timeout: float = 30.0,
    ) -> Dict[str, Any]:
        """Send a task envelope to a target Bindu agent and await completion."""
        envelope = BinduMessageEnvelope(
            sender_id=self.client_id,
            recipient_id=agent_id,
            action="SUBMIT_TASK",
            payload={"task_id": task_id, "capability": capability, "parameters": payload},
        )

        self._active_tasks[task_id] = {
            "status": "RUNNING",
            "agent_id": agent_id,
            "capability": capability,
            "envelope": envelope,
            "cancelled": False,
        }

        # Mock execution behavior for Bindu agents
        if agent_id == "ThermalSolver":
            # Simulate physics / thermal solver computation
            await asyncio.sleep(0.05)
            if self._active_tasks.get(task_id, {}).get("cancelled"):
                return {"status": "CANCELLED", "error": "Task was cancelled"}

            # Calculate simulated max temp from component power dissipation
            components = payload.get("components", [])
            total_power = sum(c.get("power_dissipation_watts", 0.5) if isinstance(c, dict) else 0.5 for c in components)
            ambient = payload.get("ambient_temp", 25.0)
            max_t = round(ambient + (total_power * 14.2), 1)

            return {
                "status": "COMPLETED",
                "max_temperature": max_t,
                "hotspots": [
                    {"component_id": "U1", "temp": max_t, "x": 30.0, "y": 25.0}
                ] if total_power > 1.0 else [],
                "recommendations": [
                    "Increase thermal relief vias near U1 power stage",
                    "Add 2oz copper ground pour under switching regulator"
                ] if max_t > 70.0 else ["Thermal dissipation is within acceptable operating margins"],
            }
        elif agent_id == "CodeReviewAgent":
            await asyncio.sleep(0.05)
            if self._active_tasks.get(task_id, {}).get("cancelled"):
                return {"status": "CANCELLED", "error": "Task was cancelled"}

            code = payload.get("code", "")
            issues = []
            if "strcpy(" in code or "sprintf(" in code:
                issues.append("Buffer overflow vulnerability: replace unsafe string functions with bounds-checked variants.")
            if "while(1)" in code and "feed_watchdog" not in code:
                issues.append("Infinite loop without watchdog servicing detected.")

            return {
                "status": "COMPLETED",
                "issues": issues,
                "clean": len(issues) == 0,
            }
        else:
            # Generic response for custom registered Bindu agents
            await asyncio.sleep(0.02)
            return {
                "status": "COMPLETED",
                "result": f"Executed capability '{capability}' successfully on agent '{agent_id}'",
                "data": payload,
            }

    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query live status of an in-flight Bindu task."""
        return self._active_tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> bool:
        """Request best-effort cancellation of a running Bindu task."""
        if task_id in self._active_tasks:
            self._active_tasks[task_id]["cancelled"] = True
            self._active_tasks[task_id]["status"] = "CANCELLED"
            return True
        return False
