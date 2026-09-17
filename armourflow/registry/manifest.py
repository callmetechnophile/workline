"""Agent manifest schema according to ArmourFlow platform specification."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AgentManifest(BaseModel):
    """Authoritative discoverable manifest for a platform agent."""

    agent_id: str = Field(..., description="Unique platform ID (e.g. 'agent.24', 'agent.01')")
    alias_id: Optional[str] = Field(default=None, description="Legacy alias (e.g. 'Agent #24')")
    name: str = Field(..., description="Canonical agent class / display name")
    version: str = Field(default="1.0.0", description="SemVer implementation version")
    description: str = Field(..., description="Functional domain responsibility")
    capabilities: List[str] = Field(default_factory=list, description="Supported domain capability tags")
    entrypoint: str = Field(..., description="Python module import path (module:Class)")
    health: str = Field(default="HEALTHY", description="Operational health status: HEALTHY, DEGRADED, UNAVAILABLE")
    dependencies: List[str] = Field(default_factory=list, description="Internal and external dependencies")
    permissions: List[str] = Field(default_factory=list, description="Required ArmorIQ scopes")
    execution_level: str = Field(default="read_only", description="read_only, isolated_execution, or privileged_execution")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected input structure definition")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="Expected output structure definition")
