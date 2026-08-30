"""
Agent #14 lifecycle orchestrator client for EngineeringCopilotAgent (Section 41).
Interfaces with ProjectLifecycleOrchestrator for lifecycle state, next actions, and human approvals.
"""

from typing import Any, Dict, List, Optional
from research_agents.project_lifecycle_orchestrator.agent import ProjectLifecycleOrchestrator
from research_agents.project_lifecycle_orchestrator.providers.mock_provider import MockOrchestratorProvider
from research_agents.project_lifecycle_orchestrator.schemas import (
    BlockerObject,
    HumanRequestObject,
    NextAction,
    OrchestrationInput,
    ProjectHealthObject,
    RevalidationPlan,
)


class ProjectLifecycleClient:
    """Client wrapper interfacing with Agent #14 (ProjectLifecycleOrchestrator)."""

    def __init__(self, orchestrator: Optional[ProjectLifecycleOrchestrator] = None):
        self.orchestrator = orchestrator or ProjectLifecycleOrchestrator(
            reasoning_provider=MockOrchestratorProvider()
        )

    async def get_next_action_async(self, project_id: str, current_state: str = "QA", qa_status: str = "VERIFIED") -> NextAction:
        inp = OrchestrationInput(project_id=project_id)
        out = await self.orchestrator.run(inp, qa_status=qa_status)
        return out.next_action

    def get_next_action(self, project_id: str, current_state: str = "QA", qa_status: str = "VERIFIED") -> NextAction:
        inp = OrchestrationInput(project_id=project_id)
        out = self.orchestrator.run_sync(inp, qa_status=qa_status)
        return out.next_action

    def get_project_health(self, project_id: str) -> ProjectHealthObject:
        return self.orchestrator.get_project_health(project_id)

    def get_blockers(self, project_id: str) -> List[BlockerObject]:
        return self.orchestrator.evaluate_blockers(project_id)

    def get_revalidation_scope(self, change_type: str, artifact_id: str) -> RevalidationPlan:
        return self.orchestrator.determine_revalidation_scope(change_type, artifact_id)

    def request_human_approval(self, project_id: str, reason: str, decision: str) -> HumanRequestObject:
        return self.orchestrator.request_human_decision(project_id, reason, decision)
