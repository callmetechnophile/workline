"""
Action proposal management for EngineeringCopilotAgent (Sections 36–40, 64, 80).
Converts natural language commands into safe ActionProposal structures routed to Agent #14 without direct execution.
"""

from typing import List, Optional
import uuid
from loguru import logger
from research_agents.engineering_copilot.schemas import ActionProposal


class ActionProposalManager:
    """Creates auditable action proposals for privileged actions."""

    def create_action_proposal(
        self,
        project_id: str,
        requested_action: str,
        target_agent: str = "EngineeringExecutionAgent",
        reason: str = "User requested task execution via Copilot interface.",
        affected_objects: Optional[List[str]] = None,
        is_destructive: bool = False,
    ) -> ActionProposal:
        prop_id = f"PROP-{uuid.uuid4().hex[:6].upper()}"
        requires_human = is_destructive or "deploy" in requested_action.lower() or "delete" in requested_action.lower()

        proposal = ActionProposal(
            proposal_id=prop_id,
            project_id=project_id,
            requested_action=requested_action,
            target_agent=target_agent,
            reason=reason,
            affected_objects=affected_objects or [],
            requires_validation=True,
            requires_authorization=True,
            requires_human_approval=requires_human,
            status="pending",
        )

        logger.info(f"Created ActionProposal [{prop_id}] for project '{project_id}': '{requested_action}' -> '{target_agent}' (HumanRequired={requires_human})")
        return proposal
