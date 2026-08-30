"""
Revalidation engine for ProjectLifecycleOrchestrator (Sections 34–37).
Calculates minimum necessary downstream revalidation without unnecessarily restarting the entire pipeline.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from research_agents.project_lifecycle_orchestrator.schemas import (
    LifecycleStateLiteral,
    RevalidationPlan,
    StaleObject,
)


class RevalidationEngine:
    """Computes targeted change propagation and manages stale artifact markers."""

    def determine_revalidation_scope(
        self,
        change_type: str,
        artifact_id: str,
        details: str = "",
    ) -> RevalidationPlan:
        ct_upper = change_type.upper()

        # 1. Documentation-Only Change (Section 34 & 54)
        if "DOCUMENTATION" in ct_upper or "DOCS" in ct_upper or "README" in ct_upper:
            return RevalidationPlan(
                trigger_artifact=artifact_id,
                trigger_type=change_type,
                affected_subsystems=[],
                affected_components=[],
                affected_tasks=[],
                affected_tests=[],
                required_stages=[],  # Zero engineering revalidation
                human_approval_needed=False,
            )

        # 2. Firmware / Software Change (Section 34)
        elif "FIRMWARE" in ct_upper or "CODE" in ct_upper or "SOFTWARE" in ct_upper:
            return RevalidationPlan(
                trigger_artifact=artifact_id,
                trigger_type=change_type,
                affected_subsystems=["ThermalImagingSubsystem"],
                affected_components=[],
                affected_tasks=["TASK-001"],
                affected_tests=["TEST-001"],
                required_stages=["IMPLEMENTATION", "QA"],
                human_approval_needed=False,
            )

        # 3. Component Change (Section 34 & 55)
        elif "COMPONENT" in ct_upper or "PART" in ct_upper or "BOM" in ct_upper:
            return RevalidationPlan(
                trigger_artifact=artifact_id,
                trigger_type=change_type,
                affected_subsystems=["ThermalImagingSubsystem", "PowerSubsystem"],
                affected_components=[artifact_id],
                affected_tasks=["TASK-001", "TASK-002"],
                affected_tests=["TEST-001"],
                required_stages=["BOM", "VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
                human_approval_needed=False,
            )

        # 4. Architecture / Protocol Change (Section 34 & 53)
        elif "ARCHITECTURE" in ct_upper or "PROTOCOL" in ct_upper or "INTERFACE" in ct_upper:
            return RevalidationPlan(
                trigger_artifact=artifact_id,
                trigger_type=change_type,
                affected_subsystems=["ThermalImagingSubsystem", "EdgeInferenceSubsystem"],
                affected_components=["500-0771-01", "945-13766-0000-000"],
                affected_tasks=["TASK-001", "TASK-002"],
                affected_tests=["TEST-001", "TEST-002"],
                required_stages=["ARCHITECTURE", "BOM", "VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
                human_approval_needed=True,
            )

        # Default full downstream
        return RevalidationPlan(
            trigger_artifact=artifact_id,
            trigger_type=change_type,
            required_stages=["VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
            human_approval_needed=False,
        )

    def mark_stale_artifacts(
        self,
        plan: RevalidationPlan,
        superseded_version: str = "v1.0.0",
    ) -> List[StaleObject]:
        stale_items: List[StaleObject] = []
        now_str = datetime.now(timezone.utc).isoformat()

        for t in plan.affected_tasks:
            stale_items.append(
                StaleObject(
                    artifact_id=t,
                    artifact_type="implementation_task",
                    superseded_by=superseded_version,
                    status="stale",
                    reason=f"Upstream change in {plan.trigger_artifact} ({plan.trigger_type}) requires task replanning.",
                    timestamp=now_str,
                )
            )

        for test in plan.affected_tests:
            stale_items.append(
                StaleObject(
                    artifact_id=test,
                    artifact_type="test_result",
                    superseded_by=superseded_version,
                    status="invalidated",
                    reason=f"Test verification invalidated by upstream change in {plan.trigger_artifact}.",
                    timestamp=now_str,
                )
            )

        return stale_items
