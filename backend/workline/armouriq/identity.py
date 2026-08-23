"""
ArmourIQ Agent Identity: Establishes cryptographic identity and capability profiles for ADK agents.
"""

from datetime import datetime, timezone
import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from backend.workline.armouriq.capabilities import AgentCapability, RiskTier


SECRET_SALT = b"armouriq-adk-agent-trust-key-2026"


class AgentIdentity(BaseModel):
    """ArmourIQ Agent Identity definition governing an active ADK agent."""
    agent_id: str = Field(..., description="Unique agent identifier (e.g. 'workline.research_agent')")
    agent_type: str = Field(..., description="Classification category (e.g. 'research', 'planner', 'builder')")
    project_id: str = Field(..., description="Authorized project boundary")
    owner_id: str = Field(default="default_user", description="Owner or authenticated user issuing the task")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Explicit granted capabilities")
    trust_level: str = Field(default="TRUSTED", description="Trust classification: TRUSTED, RESTRICTED, UNTRUSTED")
    policy_profile: str = Field(default="standard_engineering", description="Policy profile applied to this agent")
    session_id: str = Field(..., description="Session boundary identifier")
    created_at: float = Field(default_factory=time.time)
    token_signature: Optional[str] = None

    def sign(self) -> str:
        """Calculates HMAC signature ensuring tamper-proof agent identity."""
        cap_str = ",".join(sorted([c.value for c in self.capabilities]))
        payload = f"{self.agent_id}|{self.agent_type}|{self.project_id}|{self.owner_id}|{cap_str}|{self.session_id}|{self.created_at}"
        mac = hmac.new(SECRET_SALT, payload.encode("utf-8"), hashlib.sha256)
        self.token_signature = mac.hexdigest()
        return self.token_signature

    def verify(self) -> bool:
        """Verifies integrity of the agent identity token."""
        if not self.token_signature:
            return False
        cap_str = ",".join(sorted([c.value for c in self.capabilities]))
        payload = f"{self.agent_id}|{self.agent_type}|{self.project_id}|{self.owner_id}|{cap_str}|{self.session_id}|{self.created_at}"
        expected = hmac.new(SECRET_SALT, payload.encode("utf-8"), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, self.token_signature)


# Canonical ADK Agent Capability Profiles
CANONICAL_AGENT_PROFILES: Dict[str, Dict[str, Any]] = {
    "root_orchestrator": {
        "agent_type": "orchestrator",
        "capabilities": [
            AgentCapability.READ_RESEARCH,
            AgentCapability.READ_KNOWLEDGE,
            AgentCapability.READ_DATASHEET,
            AgentCapability.READ_PROJECT,
            AgentCapability.LOOKUP_COMPONENT,
            AgentCapability.ANALYZE_COMPONENT,
            AgentCapability.RUN_SIMULATION,
            AgentCapability.VALIDATE_PCB,
            AgentCapability.UPDATE_PROJECT_STATE,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "orchestrator_governance",
    },
    "planner_agent": {
        "agent_type": "planner",
        "capabilities": [
            AgentCapability.READ_RESEARCH,
            AgentCapability.READ_KNOWLEDGE,
            AgentCapability.READ_PROJECT,
            AgentCapability.UPDATE_PROJECT_STATE,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "planner_governance",
    },
    "domain_researcher": {
        "agent_type": "researcher",
        "capabilities": [
            AgentCapability.READ_RESEARCH,
            AgentCapability.READ_KNOWLEDGE,
            AgentCapability.READ_DATASHEET,
            AgentCapability.READ_PROJECT,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "research_read_only",
    },
    "research_agent": {
        "agent_type": "researcher",
        "capabilities": [
            AgentCapability.READ_RESEARCH,
            AgentCapability.READ_KNOWLEDGE,
            AgentCapability.READ_DATASHEET,
            AgentCapability.READ_PROJECT,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "research_read_only",
    },
    "innovation_agent": {
        "agent_type": "researcher",
        "capabilities": [
            AgentCapability.READ_RESEARCH,
            AgentCapability.READ_KNOWLEDGE,
            AgentCapability.READ_PROJECT,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "research_read_only",
    },
    "timeline_agent": {
        "agent_type": "planner",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.UPDATE_PROJECT_STATE,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "planning_only",
    },
    "builder_agent": {
        "agent_type": "builder",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.LOOKUP_COMPONENT,
            AgentCapability.ANALYZE_COMPONENT,
            AgentCapability.OPTIMIZE_BOM,
            AgentCapability.MODIFY_BOM,
            AgentCapability.RUN_SIMULATION,
            AgentCapability.VALIDATE_PCB,
            AgentCapability.MODIFY_PCB,
            AgentCapability.UPDATE_PROJECT_STATE,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "hardware_engineering",
    },
    "bom_agent": {
        "agent_type": "builder",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.LOOKUP_COMPONENT,
            AgentCapability.OPTIMIZE_BOM,
            AgentCapability.MODIFY_BOM,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "bom_optimization",
    },
    "pcb_agent": {
        "agent_type": "builder",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.VALIDATE_PCB,
            AgentCapability.MODIFY_PCB,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "pcb_engineering",
    },
    "validation_agent": {
        "agent_type": "validator",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.LOOKUP_COMPONENT,
            AgentCapability.ANALYZE_COMPONENT,
            AgentCapability.RUN_SIMULATION,
            AgentCapability.VALIDATE_PCB,
        ],
        "trust_level": "TRUSTED",
        "policy_profile": "deterministic_validation",
    },
    "procurement_agent": {
        "agent_type": "procurement",
        "capabilities": [
            AgentCapability.READ_PROJECT,
            AgentCapability.LOOKUP_COMPONENT,
            AgentCapability.CREATE_PROCUREMENT_QUOTE,
            # Note: EXECUTE_PROCUREMENT is restricted and requires human approval
        ],
        "trust_level": "RESTRICTED",
        "policy_profile": "procurement_safety",
    },
}


class AgentIdentityManager:
    """Factory and registry for verifiable ArmourIQ Agent Identities."""

    @classmethod
    def create_agent_identity(
        cls,
        agent_id: str,
        project_id: str,
        session_id: str,
        owner_id: str = "default_user",
        custom_capabilities: Optional[List[AgentCapability]] = None,
        trust_level: Optional[str] = None,
    ) -> AgentIdentity:
        """Create and cryptographically sign an ArmourIQ agent identity."""
        profile_key = agent_id.replace("workline.", "")
        profile = CANONICAL_AGENT_PROFILES.get(profile_key, {
            "agent_type": "custom_agent",
            "capabilities": [AgentCapability.READ_PROJECT, AgentCapability.READ_KNOWLEDGE],
            "trust_level": "RESTRICTED",
            "policy_profile": "standard_engineering",
        })

        caps = custom_capabilities if custom_capabilities is not None else list(profile["capabilities"])
        t_level = trust_level or profile.get("trust_level", "TRUSTED")

        identity = AgentIdentity(
            agent_id=agent_id,
            agent_type=profile.get("agent_type", "worker"),
            project_id=project_id,
            owner_id=owner_id,
            capabilities=caps,
            trust_level=t_level,
            policy_profile=profile.get("policy_profile", "standard_engineering"),
            session_id=session_id,
        )
        identity.sign()
        return identity
