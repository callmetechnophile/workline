"""Policy engine and authorization checks for external agent invocations."""

from typing import Any, Dict, Optional, Tuple
from backend.workline.interoperability.capabilities import AgentCapability, RiskLevel
from backend.workline.interoperability.registry import ExternalAgent


class PolicyEngine:
    """Evaluates whether an external task invocation is authorized under Workline policy."""

    @classmethod
    def evaluate_task_authorization(
        cls,
        project_id: str,
        team_id: str,
        requesting_agent: str,
        target_agent: ExternalAgent,
        capability: AgentCapability,
        actor_id: Optional[str] = None,
        human_approved: bool = False,
    ) -> Tuple[bool, Optional[str]]:
        """Evaluate if the task is authorized to run.
        
        Returns:
            (is_authorized, rejection_reason)
        """
        # 1. Project & Team Identity Verification
        if not project_id or not project_id.strip():
            return False, "Invalid or missing project_id"
        if not team_id or not team_id.strip():
            return False, "Invalid or missing team_id"

        # 2. Target Agent Status
        if target_agent.status.value != "AVAILABLE":
            return False, f"Target agent '{target_agent.agent_id}' is not available (status: {target_agent.status.value})"

        # 3. Capability Availability
        if not capability.availability:
            return False, f"Capability '{capability.capability_id}' is currently disabled on agent '{target_agent.agent_id}'"

        # 4. Critical & High Risk Governance
        if capability.risk_level == RiskLevel.CRITICAL:
            if not human_approved:
                return False, f"CRITICAL risk capability '{capability.capability_id}' requires explicit human authorization."

        if capability.risk_level == RiskLevel.HIGH:
            if not human_approved:
                return False, f"HIGH risk capability '{capability.capability_id}' requires user confirmation before execution."

        return True, None
