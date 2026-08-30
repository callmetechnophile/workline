"""
Failure classification and routing service for ProjectLifecycleOrchestrator (Sections 19–22).
Directs failures to the correct upstream engineering agent without allowing execution agents to redesign systems.
"""

from typing import Dict, List
from research_agents.project_lifecycle_orchestrator.schemas import NextAction


class FailureRouter:
    """Classifies QA and validation failures into deterministic remediation workflows."""

    def route_failure(
        self,
        project_id: str,
        failure_type: str,
        failure_details: str,
    ) -> NextAction:
        ft_upper = failure_type.upper()

        # 1. BOM Failure Loop (Section 22)
        if "BOM" in ft_upper or "SUBSTITUTE" in ft_upper or "PART" in ft_upper:
            return NextAction(
                action_id=f"ACT-CORR-BOM-{project_id}",
                project_id=project_id,
                current_state="QA",
                next_state="BOM",
                action_type="OPTIMIZE_BOM",
                target_agent="BOMOptimizationAgent",
                reason=f"BOM Conformance Failure: {failure_details}. Routing to Agent #8 for BOM revision before revalidation.",
                required_authorization=[],
                human_approval_required=False,
                priority="critical",
            )

        # 2. Architecture Failure Loop (Section 21)
        elif "ARCHITECTURE" in ft_upper or "CONFORMANCE" in ft_upper or "INTERFACE" in ft_upper:
            return NextAction(
                action_id=f"ACT-CORR-ARCH-{project_id}",
                project_id=project_id,
                current_state="QA",
                next_state="ARCHITECTURE",
                action_type="DESIGN",
                target_agent="EngineeringArchitectureAgent",
                reason=f"Architecture Conformance Failure: {failure_details}. Routing to Agent #6 for architecture review before revalidation.",
                required_authorization=[],
                human_approval_required=False,
                priority="critical",
            )

        # 3. Test Failure Loop (Section 19)
        elif "TEST" in ft_upper or "PYTEST" in ft_upper:
            return NextAction(
                action_id=f"ACT-CORR-TEST-{project_id}",
                project_id=project_id,
                current_state="QA",
                next_state="PLANNING",
                action_type="PLAN_IMPLEMENTATION",
                target_agent="ProjectExecutionAgent",
                reason=f"Test Failure: {failure_details}. Routing to Agent #10 to generate remediation task plan.",
                required_authorization=[],
                human_approval_required=False,
                priority="high",
            )

        # Default implementation correction
        return NextAction(
            action_id=f"ACT-CORR-GEN-{project_id}",
            project_id=project_id,
            current_state="QA",
            next_state="PLANNING",
            action_type="PLAN_IMPLEMENTATION",
            target_agent="ProjectExecutionAgent",
            reason=f"Engineering Quality Failure: {failure_details}. Re-planning implementation.",
            required_authorization=[],
            human_approval_required=False,
            priority="high",
        )
