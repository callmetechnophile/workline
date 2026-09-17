"""
Agent manifest, health, and capability GraphQL types.
"""

from typing import List, Optional
import strawberry


@strawberry.type
class AgentManifestType:
    agent_id: str
    name: str
    version: str
    execution_level: str
    entrypoint: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    permissions: List[str]


@strawberry.type
class AgentHealthType:
    agent_id: str
    status: str
    importable: bool
    error: Optional[str] = None


@strawberry.type
class CapabilityType:
    capability: str
    agent_id: str
    agent_name: str
