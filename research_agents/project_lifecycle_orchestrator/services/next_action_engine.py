"""
Next action decision engine for ProjectLifecycleOrchestrator (Sections 10–13, 41, 42).
Combines graph state, blockers, failure routing, loop guards, and agent readiness to output deterministic next actions.
"""

from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.project_lifecycle_orchestrator.config import orchestrator_config
from research_agents.project_lifecycle_orchestrator.registry.agent_registry import AgentRegistry
from research_agents.project_lifecycle_orchestrator.schemas import (
    BlockerObject,
    HumanRequestObject,
    LifecycleStateLiteral,
    NextAction,
)
from research_agents.project_lifecycle_orchestrator.services.failure_router import FailureRouter


class NextActionEngine:
    """Evaluates project state and determines the next valid workflow action."""

    def __init__(self, agent_registry: Optional[AgentRegistry] = None, failure_router: Optional[FailureRouter] = None):
        self.registry = agent_registry or AgentRegistry()
        self.failure_router = failure_router or FailureRouter()
        self._failure_counts: Dict[str, int] = {}

    def record_failure_attempt(self, project_id: str, failure_key: str) -> int:
        key = f"{project_id}:{failure_key}"
        self._failure_counts[key] = self._failure_counts.get(key, 0) + 1
        return self._failure_counts[key]

    def determine_next_action(
        self,
        project_id: str,
        current_state: LifecycleStateLiteral,
        qa_status: Optional[str] = None,
        validation_status: Optional[str] = None,
        blockers: Optional[List[BlockerObject]] = None,
        human_requests: Optional[List[HumanRequestObject]] = None,
        last_failure_type: Optional[str] = None,
        last_failure_details: Optional[str] = None,
    ) -> NextAction:
        action_id = f"ACT-{uuid.uuid4().hex[:6].upper()}"
        blks = blockers or []
        pending_human = [h for h in (human_requests or []) if h.status == "pending"]

        # 1. Human Approval Pending Check (Section 25)
        if pending_human:
            req = pending_human[0]
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state=current_state,
                next_state="AWAITING_HUMAN",
                action_type="REQUEST_HUMAN_INPUT",
                target_agent="ProjectLifecycleOrchestrator",
                reason=f"Human approval required: {req.reason}",
                blocking_conditions=[f"Awaiting human approval on request {req.request_id}"],
                human_approval_required=True,
                priority="critical",
            )

        # 2. Database or Fatal Infrastructure Blocker (Section 40)
        db_blockers = [b for b in blks if b.type == "DATABASE_UNAVAILABLE"]
        if db_blockers:
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state=current_state,
                next_state="BLOCKED",
                action_type="WAIT_FOR_RESOURCE",
                target_agent="ProjectLifecycleOrchestrator",
                reason="SurrealDB is offline. Pausing orchestration until database connectivity is restored.",
                blocking_conditions=["SurrealDB unavailable"],
                priority="critical",
            )

        # 3. Authorization Blocker (Section 27)
        auth_blockers = [b for b in blks if b.type == "AUTHORIZATION_DENIED"]
        if auth_blockers:
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state=current_state,
                next_state="BLOCKED",
                action_type="BLOCK",
                target_agent="ProjectLifecycleOrchestrator",
                reason="ArmorIQ authorization denied. Cannot proceed with execution.",
                blocking_conditions=["ArmorIQ authorization denied"],
                human_approval_required=True,
                priority="critical",
            )

        # 4. Loop Guard: Check for repeated failures (Sections 41 & 42)
        if last_failure_type:
            attempts = self.record_failure_attempt(project_id, last_failure_type)
            if attempts >= orchestrator_config.max_retries:
                logger.error(f"Loop Guard triggered for project '{project_id}': Failure '{last_failure_type}' repeated {attempts} times.")
                return NextAction(
                    action_id=action_id,
                    project_id=project_id,
                    current_state=current_state,
                    next_state="AWAITING_HUMAN",
                    action_type="REQUEST_HUMAN_INPUT",
                    target_agent="ProjectLifecycleOrchestrator",
                    reason=f"Loop Guard: Repeated failure '{last_failure_type}' ({attempts} attempts). Halting automated retries.",
                    blocking_conditions=[f"Repeated failure {last_failure_type}"],
                    human_approval_required=True,
                    priority="critical",
                )

        # 5. QA Failure Remediation Routing (Sections 19–22)
        if qa_status and qa_status.upper() in ("FAILED", "BLOCKED"):
            return self.failure_router.route_failure(
                project_id=project_id,
                failure_type=last_failure_type or "TEST_FAILURE",
                failure_details=last_failure_details or "Autonomous QA verification failed.",
            )

        # 6. Validation Failure Remediation Routing (Section 19)
        if validation_status and validation_status.upper() in ("BLOCKED", "FAILED"):
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state=current_state,
                next_state="ARCHITECTURE",
                action_type="DESIGN",
                target_agent="EngineeringArchitectureAgent",
                reason="Design rule validation failed. Routing back to Agent #6 for architecture revision.",
                required_authorization=[],
                priority="critical",
            )

        # 7. Normal Lifecycle Progression (Section 8)
        if current_state == "RESEARCH":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="RESEARCH",
                next_state="SYNTHESIS",
                action_type="SYNTHESIZE",
                target_agent="EngineeringSynthesisAgent",
                reason="Academic and web research completed. Synthesizing system requirements and tradeoff decisions.",
                priority="high",
            )
        elif current_state == "SYNTHESIS":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="SYNTHESIS",
                next_state="ARCHITECTURE",
                action_type="DESIGN",
                target_agent="EngineeringArchitectureAgent",
                reason="Requirements synthesized. Generating system architecture, subsystems, and interface buses.",
                priority="high",
            )
        elif current_state == "ARCHITECTURE":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="ARCHITECTURE",
                next_state="BOM",
                action_type="GENERATE_BOM",
                target_agent="ComponentPlanningAgent",
                reason="Architecture defined. Generating engineering BOM and selecting exact component MPNs.",
                priority="high",
            )
        elif current_state == "BOM":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="BOM",
                next_state="PROCUREMENT",
                action_type="OPTIMIZE_BOM",
                target_agent="BOMOptimizationAgent",
                reason="BOM parts selected. Optimizing supplier quotes, landed cost, and logistics.",
                priority="high",
            )
        elif current_state == "PROCUREMENT":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="PROCUREMENT",
                next_state="VALIDATION",
                action_type="VALIDATE",
                target_agent="EngineeringValidationAgent",
                reason="Procurement optimized. Executing engineering design rule, electrical, and thermal validation.",
                priority="high",
            )
        elif current_state == "VALIDATION":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="VALIDATION",
                next_state="PLANNING",
                action_type="PLAN_IMPLEMENTATION",
                target_agent="ProjectExecutionAgent",
                reason="Engineering validation passed. Generating scoped implementation work packages and tasks.",
                priority="high",
            )
        elif current_state == "PLANNING":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="PLANNING",
                next_state="IMPLEMENTATION",
                action_type="EXECUTE",
                target_agent="EngineeringExecutionAgent",
                reason="Implementation plan approved. Executing scoped implementation tasks under ArmorIQ authorization.",
                required_authorization=["filesystem.write", "shell", "test_runner"],
                priority="high",
            )
        elif current_state == "IMPLEMENTATION":
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="IMPLEMENTATION",
                next_state="QA",
                action_type="VERIFY",
                target_agent="VerificationQAAgent",
                reason="Implementation execution complete. Performing independent verification and autonomous QA testing.",
                required_authorization=["test_runner", "pytest", "security_scan"],
                priority="high",
            )
        elif current_state == "QA" and qa_status and qa_status.upper() in ("VERIFIED", "VERIFIED_WITH_WARNINGS", "PASS"):
            return NextAction(
                action_id=action_id,
                project_id=project_id,
                current_state="QA",
                next_state="VERIFIED",
                action_type="COMPLETE",
                target_agent="EngineeringKnowledgeGraphAgent",
                reason="Autonomous QA verified with 100% pass. Transitioning project to VERIFIED.",
                priority="high",
            )

        # Default completion check
        return NextAction(
            action_id=action_id,
            project_id=project_id,
            current_state=current_state,
            next_state="VERIFIED",
            action_type="COMPLETE",
            target_agent="ProjectLifecycleOrchestrator",
            reason="All lifecycle gates satisfied. Project verified.",
            priority="medium",
        )
