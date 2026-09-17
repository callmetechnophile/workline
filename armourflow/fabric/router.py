"""Capability-based routing engine resolving tasks to internal or external agents."""

from typing import Optional, Tuple
from loguru import logger

from armourflow.registry.manifest import AgentManifest
from armourflow.registry.registry import AuthoritativeAgentRegistry, get_agent_registry


class CapabilityRouter:
    """
    Decoupled router: Agent -> Control Fabric -> Agent.
    Resolves target capability to candidate agents without N x N coupling.
    """

    def __init__(self, registry: Optional[AuthoritativeAgentRegistry] = None):
        self.registry = registry or get_agent_registry()

    def resolve_target(
        self,
        capability: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Tuple[Optional[AgentManifest], Optional[str]]:
        """
        Resolve task target by explicit agent_id or requested capability.
        Returns (AgentManifest, None) or (None, error_string).
        """
        # 1. Explicit Agent ID
        if agent_id:
            manifest = self.registry.get_agent(agent_id)
            if manifest:
                return manifest, None
            return None, f"AGENT_NOT_FOUND: Agent identifier '{agent_id}' does not exist in registry."

        # 2. Capability Resolution
        if capability:
            candidates = self.registry.find_by_capability(capability)
            if candidates:
                # Prefer healthy/active agents
                for c in candidates:
                    h = self.registry.check_health(c.agent_id)
                    if h.get("status") == "HEALTHY":
                        return c, None
                # Fallback to first candidate
                return candidates[0], None
            return None, f"CAPABILITY_NOT_RESOLVED: No agent provides capability '{capability}'."

        return None, "ROUTING_ERROR: Either agent_id or capability must be specified."
