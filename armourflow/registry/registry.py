"""Authoritative Agent Registry implementation with dynamic manifest discovery."""

import importlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from loguru import logger

from armourflow.registry.manifest import AgentManifest


class AuthoritativeAgentRegistry:
    """
    Single authoritative registry answering:
    - Which agents exist?
    - Which version is running?
    - Which capabilities exist?
    - Which agents are healthy?
    - Which dependencies do they require?
    - Which permissions do they require?
    - Which tasks can they execute?
    """

    _instance: Optional["AuthoritativeAgentRegistry"] = None

    def __init__(self, manifests_dir: Optional[str] = None):
        self._agents: Dict[str, AgentManifest] = {}
        self._capability_index: Dict[str, List[str]] = {}
        self._manifests_dir = manifests_dir or os.path.join(os.path.dirname(__file__), "manifests")
        self._load_all_manifests()

    @classmethod
    def get_instance(cls) -> "AuthoritativeAgentRegistry":
        if cls._instance is None:
            cls._instance = AuthoritativeAgentRegistry()
        return cls._instance

    def _load_all_manifests(self):
        """Scan manifests directory and register all agent manifests."""
        p = Path(self._manifests_dir)
        if p.exists():
            for f in sorted(p.glob("*.json")):
                try:
                    with open(f, "r", encoding="utf-8") as fp:
                        data = json.load(fp)
                        manifest = AgentManifest.model_validate(data)
                        self.register(manifest)
                except Exception as e:
                    logger.warning(f"[AgentRegistry] Failed to parse manifest {f.name}: {e}")

        logger.info(f"[AuthoritativeAgentRegistry] Loaded {len(self._agents)} agents across {len(self._capability_index)} capabilities")

    def register(self, manifest: AgentManifest):
        """Register an agent manifest and update indexes."""
        # Index by canonical agent_id (e.g. "agent.24")
        self._agents[manifest.agent_id.lower()] = manifest
        # Index by legacy alias if present (e.g. "Agent #24")
        if manifest.alias_id:
            self._agents[manifest.alias_id.lower()] = manifest
        # Index by name (e.g. "ManufacturingDFMAgent")
        self._agents[manifest.name.lower()] = manifest

        # Update capability index
        for cap in manifest.capabilities:
            cap_key = cap.lower()
            if cap_key not in self._capability_index:
                self._capability_index[cap_key] = []
            if manifest.agent_id not in self._capability_index[cap_key]:
                self._capability_index[cap_key].append(manifest.agent_id)

    def get_agent(self, identifier: str) -> Optional[AgentManifest]:
        """Look up an agent by ID ('agent.24', 'Agent #24') or name."""
        if not identifier:
            return None
        return self._agents.get(identifier.strip().lower())

    def list_agents(self) -> List[AgentManifest]:
        """Return unique list of all registered agents."""
        unique = {m.agent_id: m for m in self._agents.values()}
        return list(unique.values())

    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        """Resolve all agents that provide a specific capability."""
        cap_key = capability.strip().lower()
        agent_ids = self._capability_index.get(cap_key, [])
        return [self._agents[aid.lower()] for aid in agent_ids if aid.lower() in self._agents]

    def get_all_capabilities(self) -> List[str]:
        """Return all distinct capabilities available across the platform."""
        return sorted(list(self._capability_index.keys()))

    def check_health(self, agent_id: str) -> Dict[str, Any]:
        """Inspect and verify live health of an agent entrypoint."""
        manifest = self.get_agent(agent_id)
        if not manifest:
            return {"status": "NOT_FOUND", "agent_id": agent_id, "healthy": False}

        # Check if entrypoint is importable
        is_importable = False
        import_error = None
        try:
            module_name, class_name = manifest.entrypoint.split(":")
            mod = importlib.import_module(module_name)
            is_importable = hasattr(mod, class_name)
        except Exception as e:
            import_error = str(e)

        status = "HEALTHY" if is_importable else "DEGRADED"
        return {
            "agent_id": manifest.agent_id,
            "name": manifest.name,
            "version": manifest.version,
            "status": status,
            "entrypoint": manifest.entrypoint,
            "importable": is_importable,
            "error": import_error,
            "capabilities": manifest.capabilities,
            "permissions": manifest.permissions,
        }


def get_agent_registry() -> AuthoritativeAgentRegistry:
    return AuthoritativeAgentRegistry.get_instance()
