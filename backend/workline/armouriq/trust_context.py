"""
ArmourIQ Trust Context: Immutable execution envelope propagated across ADK agent chains and tools.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, Field

from backend.workline.armouriq.capabilities import AgentCapability, RiskTier


class TrustContext(BaseModel):
    """
    Cryptographically and logically verified context envelope traveling through the ADK execution chain.
    """
    request_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    session_id: str = Field(..., description="ADK session identifier")
    user_id: str = Field(default="default_user", description="Authenticated user ID")
    project_id: str = Field(..., description="Authenticated project scope")
    agent_id: str = Field(..., description="Current agent identifier")
    parent_agent_id: Optional[str] = Field(default=None, description="Parent agent ID in delegation chain")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Explicit granted capability set")
    trust_level: str = Field(default="TRUSTED", description="Trust level: TRUSTED, RESTRICTED, UNTRUSTED")
    risk_level: RiskTier = Field(default=RiskTier.LOW, description="Current execution risk level")
    authorization_scope: List[str] = Field(default_factory=list, description="Fine-grained resource permissions")
    delegation_chain: List[str] = Field(default_factory=list, description="Ordered delegation trail [root, parent, child]")
    timestamp: float = Field(default_factory=time.time)
    is_authenticated: bool = Field(default=True, description="Whether the initiator has authenticated credentials")
    is_human_approved: bool = Field(default=False, description="Whether human approval was explicitly granted for high-risk action")

    def spawn_child_context(
        self,
        child_agent_id: str,
        requested_capabilities: Optional[List[AgentCapability]] = None,
        risk_level: Optional[RiskTier] = None,
    ) -> "TrustContext":
        """
        Creates a child trust context enforcing the core ArmourIQ delegation invariant:
        CHILD CAPABILITIES ⊆ PARENT CAPABILITIES.
        """
        # Calculate allowed capabilities as a strict subset
        if requested_capabilities is None:
            child_caps = list(self.capabilities)
        else:
            # Intersection to prevent capability escalation
            parent_cap_set = set(self.capabilities)
            child_caps = [c for c in requested_capabilities if c in parent_cap_set]

        child_chain = list(self.delegation_chain)
        if not child_chain or child_chain[-1] != self.agent_id:
            child_chain.append(self.agent_id)
        child_chain.append(child_agent_id)

        return TrustContext(
            request_id=self.request_id,
            session_id=self.session_id,
            user_id=self.user_id,
            project_id=self.project_id,
            agent_id=child_agent_id,
            parent_agent_id=self.agent_id,
            capabilities=child_caps,
            trust_level=self.trust_level,
            risk_level=risk_level or self.risk_level,
            authorization_scope=list(self.authorization_scope),
            delegation_chain=child_chain,
            is_authenticated=self.is_authenticated,
            is_human_approved=self.is_human_approved,
        )

    def has_capability(self, capability: AgentCapability) -> bool:
        """Verify if context holds the required capability."""
        return capability in self.capabilities
