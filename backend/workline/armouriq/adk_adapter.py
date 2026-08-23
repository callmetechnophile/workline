"""
ArmourIQ ADK Adapter: Clean integration boundary binding Google ADK execution lifecycles to ArmourIQ governance.
"""

from typing import Any, Callable, Dict, List, Optional
from backend.workline.armouriq.audit import ArmourIQAuditLogger
from backend.workline.armouriq.capabilities import (
    AgentCapability,
    PolicyDecision,
    RiskTier,
    get_tool_capability_descriptor,
)
from backend.workline.armouriq.delegation import DelegationManager
from backend.workline.armouriq.identity import AgentIdentity, AgentIdentityManager
from backend.workline.armouriq.policy import ArmourIQPolicyEngine
from backend.workline.armouriq.risk import RiskEngine
from backend.workline.armouriq.trust_context import TrustContext


class ArmourIQSecurityError(PermissionError):
    """Raised when ArmourIQ denies agent, tool, or delegation execution."""
    def __init__(self, message: str, decision: PolicyDecision, risk_level: RiskTier, details: Optional[Dict[str, Any]] = None):
        self.decision = decision
        self.risk_level = risk_level
        self.details = details or {}
        super().__init__(f"ArmourIQ [{decision.value} - Risk:{risk_level.value}]: {message}")


class ArmourIQADKAdapter:
    """
    Adapter sitting between Google ADK agents and high-impact tool / service execution.
    """

    @classmethod
    def before_agent_callback(
        cls,
        identity: AgentIdentity,
        context: TrustContext,
    ) -> PolicyDecision:
        """
        Lifecycle hook invoked BEFORE an ADK agent executes.
        Verifies identity, project isolation, and policy.
        """
        decision, reason = ArmourIQPolicyEngine.evaluate_agent_execution(identity, context)

        ArmourIQAuditLogger.log_event(
            request_id=context.request_id,
            session_id=context.session_id,
            user_id=context.user_id,
            project_id=context.project_id,
            agent_id=identity.agent_id,
            parent_agent_id=context.parent_agent_id,
            risk_level=context.risk_level,
            policy="agent_execution_policy",
            decision=decision,
            delegation_chain=context.delegation_chain,
            execution_status="ALLOWED" if decision == PolicyDecision.ALLOW else "DENIED",
            error=reason,
            metadata={"agent_type": identity.agent_type, "trust_level": identity.trust_level},
        )

        if decision == PolicyDecision.DENY:
            raise ArmourIQSecurityError(
                message=reason or "Agent execution denied by ArmourIQ policy",
                decision=decision,
                risk_level=context.risk_level,
            )

        return decision

    @classmethod
    def after_agent_callback(
        cls,
        identity: AgentIdentity,
        context: TrustContext,
        output_summary: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Lifecycle hook invoked AFTER an ADK agent completes.
        Closes audit trust chain and records execution summary.
        """
        ArmourIQAuditLogger.log_event(
            request_id=context.request_id,
            session_id=context.session_id,
            user_id=context.user_id,
            project_id=context.project_id,
            agent_id=identity.agent_id,
            parent_agent_id=context.parent_agent_id,
            risk_level=context.risk_level,
            policy="agent_completion_audit",
            decision=PolicyDecision.ALLOW,
            delegation_chain=context.delegation_chain,
            execution_status="COMPLETED" if not error else "FAILED",
            error=error,
            metadata={"summary": output_summary[:100] if output_summary else ""},
        )

    @classmethod
    def before_tool_callback(
        cls,
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        context: TrustContext,
    ) -> PolicyDecision:
        """
        Lifecycle hook invoked BEFORE an ADK tool runs.
        Verifies capability clearance, risk tier, and human approval for critical actions.
        """
        descriptor = get_tool_capability_descriptor(tool_name)
        risk = RiskEngine.evaluate_tool_risk(tool_name, parameters, context)
        cap = descriptor.get("capability")

        decision, reason = ArmourIQPolicyEngine.evaluate_tool_execution(tool_name, parameters, context)

        ArmourIQAuditLogger.log_event(
            request_id=context.request_id,
            session_id=context.session_id,
            user_id=context.user_id,
            project_id=context.project_id,
            agent_id=context.agent_id,
            parent_agent_id=context.parent_agent_id,
            tool_name=tool_name,
            capability=cap.value if cap else None,
            risk_level=risk,
            policy="tool_authorization_policy",
            decision=decision,
            delegation_chain=context.delegation_chain,
            execution_status="AUTHORIZED" if decision == PolicyDecision.ALLOW else "BLOCKED",
            error=reason,
            metadata={"service": descriptor.get("service", "UNKNOWN")},
        )

        if decision == PolicyDecision.DENY:
            raise ArmourIQSecurityError(
                message=reason or f"Tool '{tool_name}' execution denied by ArmourIQ policy",
                decision=decision,
                risk_level=risk,
            )

        if decision == PolicyDecision.REQUIRE_APPROVAL:
            raise ArmourIQSecurityError(
                message=reason or f"Tool '{tool_name}' requires human decision approval",
                decision=decision,
                risk_level=risk,
            )

        return decision

    @classmethod
    def after_tool_callback(
        cls,
        tool_name: str,
        parameters: Optional[Dict[str, Any]],
        context: TrustContext,
        result: Any = None,
        error: Optional[str] = None,
    ) -> None:
        """
        Lifecycle hook invoked AFTER tool execution.
        Records sanitized output metadata and closes tool audit.
        """
        descriptor = get_tool_capability_descriptor(tool_name)
        risk = descriptor.get("risk", RiskTier.LOW)

        ArmourIQAuditLogger.log_event(
            request_id=context.request_id,
            session_id=context.session_id,
            user_id=context.user_id,
            project_id=context.project_id,
            agent_id=context.agent_id,
            parent_agent_id=context.parent_agent_id,
            tool_name=tool_name,
            capability=descriptor.get("capability", {}).value if hasattr(descriptor.get("capability"), "value") else None,
            risk_level=risk,
            policy="tool_execution_audit",
            decision=PolicyDecision.ALLOW,
            delegation_chain=context.delegation_chain,
            execution_status="EXECUTED" if not error else "FAILED",
            error=error,
            metadata={"service": descriptor.get("service")},
        )
