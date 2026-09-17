"""Authoritative Platform Agent Registry."""

from armourflow.registry.manifest import AgentManifest
from armourflow.registry.registry import AuthoritativeAgentRegistry, get_agent_registry

__all__ = ["AgentManifest", "AuthoritativeAgentRegistry", "get_agent_registry"]
