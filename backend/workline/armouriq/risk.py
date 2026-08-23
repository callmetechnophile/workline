"""
ArmourIQ Risk Engine: Evaluates operational risk tiers and clearance thresholds for ADK tools.
"""

from typing import Any, Dict, List, Optional
from backend.workline.armouriq.capabilities import AgentCapability, RiskTier, get_tool_capability_descriptor
from backend.workline.armouriq.trust_context import TrustContext


class RiskEngine:
    """Evaluates dynamic risk for agent tasks and tool calls."""

    @classmethod
    def evaluate_tool_risk(
        cls,
        tool_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        context: Optional[TrustContext] = None,
    ) -> RiskTier:
        """Determines the risk classification tier for a tool execution."""
        descriptor = get_tool_capability_descriptor(tool_name)
        base_risk = descriptor.get("risk", RiskTier.HIGH)

        # Dynamic risk escalation based on parameter analysis
        if parameters:
            # Side-effecting writes or external order executions are escalated
            if "order" in tool_name or parameters.get("action") == "order" or parameters.get("execute_purchase") is True:
                return RiskTier.CRITICAL
            if "release" in tool_name or parameters.get("action") == "create_release":
                return RiskTier.CRITICAL
            if parameters.get("estimated_cost", 0) > 1000.0:
                return RiskTier.CRITICAL

        return base_risk

    @classmethod
    def requires_human_approval(cls, risk: RiskTier) -> bool:
        """Returns True if the risk tier necessitates explicit human approval."""
        return risk in (RiskTier.HIGH, RiskTier.CRITICAL)
