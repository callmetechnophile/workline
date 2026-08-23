"""
ArmourIQ Policy Engine: Authoritative governance rules for ADK agents and tools.
"""

from typing import Any, Dict, List, Optional, Tuple
from backend.workline.armouriq.capabilities import (
    AgentCapability,
    PolicyDecision,
    RiskTier,
    get_tool_capability_descriptor,
)
from backend.workline.armouriq.identity import AgentIdentity
from backend.workline.armouriq.risk import RiskEngine
from backend.workline.armouriq.trust_context import TrustContext


class ArmourIQPolicyEngine:
    """Evaluates granular security and trust policies across ADK execution lifecycles."""

    @classmethod
    def evaluate_agent_execution(
        cls,
        identity: AgentIdentity,
        context: TrustContext,
    ) -> Tuple[PolicyDecision, Optional[str]]:
        """
        Evaluate if an agent is authorized to initialize and run within the project context.
        """
        # 1. Verify user authentication
        if not context.is_authenticated:
            return PolicyDecision.DENY, "Unauthenticated execution context"

        # 2. Verify project isolation
        if identity.project_id != context.project_id:
            return (
                PolicyDecision.DENY,
                f"Project mismatch: Agent project '{identity.project_id}' != Context project '{context.project_id}'",
            )

        # 3. Cryptographic token integrity
        if not identity.verify():
            return PolicyDecision.DENY, "Agent identity token verification failed"

        # 4. Trust level evaluation
        if identity.trust_level == "UNTRUSTED":
            return PolicyDecision.DENY, f"Agent '{identity.agent_id}' is marked UNTRUSTED"

        return PolicyDecision.ALLOW, None

    @classmethod
    def evaluate_tool_execution(
        cls,
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        context: TrustContext,
    ) -> Tuple[PolicyDecision, Optional[str]]:
        """
        Evaluate if the agent holds the required capability and clearance to execute a tool.
        """
        # 1. Project Isolation Check
        if not context.project_id:
            return PolicyDecision.DENY, "No authorized project context"

        # 2. Resolve required capability and risk tier
        descriptor = get_tool_capability_descriptor(tool_name)
        required_cap = descriptor.get("capability")
        risk = RiskEngine.evaluate_tool_risk(tool_name, parameters, context)

        # 3. Capability Verification
        if required_cap and not context.has_capability(required_cap):
            return (
                PolicyDecision.DENY,
                f"Capability violation: Agent '{context.agent_id}' lacks required capability '{required_cap.value}' for tool '{tool_name}'",
            )

        # 4. Critical Risk & Human Approval Governance
        if risk == RiskTier.CRITICAL:
            if not context.is_human_approved:
                return (
                    PolicyDecision.REQUIRE_APPROVAL,
                    f"CRITICAL risk action '{tool_name}' requires explicit human checkpoint approval before execution.",
                )

        # 5. Specific Domain Deny Policies
        # Research agents can never perform write-modifications or purchases
        if "research" in context.agent_id:
            if required_cap in (
                AgentCapability.EXECUTE_PROCUREMENT,
                AgentCapability.CREATE_RELEASE,
                AgentCapability.MODIFY_BOM,
                AgentCapability.MODIFY_PCB,
            ):
                return (
                    PolicyDecision.DENY,
                    f"Domain Policy: Research agent '{context.agent_id}' is strictly forbidden from executing destructive or procurement actions.",
                )

        # BOM agents can optimize/modify BOM, but can never directly execute procurement purchases
        if "bom" in context.agent_id:
            if required_cap == AgentCapability.EXECUTE_PROCUREMENT:
                return (
                    PolicyDecision.DENY,
                    f"Domain Policy: BOM agent '{context.agent_id}' is forbidden from executing direct distributor orders.",
                )

        return PolicyDecision.ALLOW, None

    @classmethod
    def evaluate_a2a_invocation(
        cls,
        caller_context: TrustContext,
        target_agent_id: str,
        target_project_id: str,
        requested_capabilities: List[AgentCapability],
    ) -> Tuple[PolicyDecision, Optional[str]]:
        """
        Evaluate cross-agent (A2A) invocation and trust propagation.
        """
        # 1. Project Isolation
        if caller_context.project_id != target_project_id:
            return (
                PolicyDecision.DENY,
                f"Cross-project A2A invocation denied: caller project '{caller_context.project_id}' != target project '{target_project_id}'",
            )

        # 2. Capability Escalation Prevention: Child ⊆ Parent
        parent_cap_set = set(caller_context.capabilities)
        escalations = [c for c in requested_capabilities if c not in parent_cap_set]
        if escalations:
            return (
                PolicyDecision.DENY,
                f"A2A capability escalation denied: target requested {escalations} which caller does not possess",
            )

        return PolicyDecision.ALLOW, None
