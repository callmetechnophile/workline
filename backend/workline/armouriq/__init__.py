"""
ArmourIQ: Enterprise Trust, Identity, Delegation, Policy, and Audit layer for Google ADK.
"""

from backend.workline.armouriq.adk_adapter import ArmourIQADKAdapter, ArmourIQSecurityError
from backend.workline.armouriq.api import router as armouriq_router
from backend.workline.armouriq.audit import ArmourIQAuditEvent, ArmourIQAuditLogger
from backend.workline.armouriq.capabilities import (
    AgentCapability,
    PolicyDecision,
    RiskTier,
    get_tool_capability_descriptor,
)
from backend.workline.armouriq.delegation import DelegationManager, DelegationViolationError
from backend.workline.armouriq.health import ArmourIQHealthService
from backend.workline.armouriq.identity import (
    CANONICAL_AGENT_PROFILES,
    AgentIdentity,
    AgentIdentityManager,
)
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.risk import RiskEngine
from backend.workline.armouriq.trust_context import TrustContext

__all__ = [
    "ArmourIQADKAdapter",
    "ArmourIQSecurityError",
    "armouriq_router",
    "ArmourIQAuditEvent",
    "ArmourIQAuditLogger",
    "AgentCapability",
    "PolicyDecision",
    "RiskTier",
    "get_tool_capability_descriptor",
    "DelegationManager",
    "DelegationViolationError",
    "ArmourIQHealthService",
    "CANONICAL_AGENT_PROFILES",
    "AgentIdentity",
    "AgentIdentityManager",
    "ArmourIQPolicyEngine",
    "RiskEngine",
    "TrustContext",
]
