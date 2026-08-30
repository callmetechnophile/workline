"""
Minimum necessary revalidation calculation for EngineeringChangeControlAgent (Sections 26 & 27).
"""

from typing import List
from research_agents.engineering_change_control.schemas import ChangePlan, ChangeRequest, ImpactObject


class ChangeRevalidationEngine:
    """Calculates minimal necessary revalidation stages without restarting the entire pipeline."""

    def create_revalidation_plan(self, change: ChangeRequest, impact: ImpactObject) -> ChangePlan:
        steps: List[str] = []
        auth: List[str] = []
        approvals: List[str] = []

        if "ARCHITECTURE" in impact.revalidation_required:
            steps.append("1. Re-evaluate architecture interfaces via Agent #6")
            approvals.append("ARCHITECTURE_REVIEW")

        if "BOM" in impact.revalidation_required:
            steps.append("2. Re-optimize BOM and verify manufacturer datasheets via Agent #8")

        if "VALIDATION" in impact.revalidation_required:
            steps.append("3. Execute engineering design rule validation gate via Agent #9")

        if "PLANNING" in impact.revalidation_required:
            steps.append("4. Update implementation work package plan via Agent #10")

        if "IMPLEMENTATION" in impact.revalidation_required:
            steps.append("5. Apply implementation changes via Agent #11 under ArmorIQ authority")
            auth.append("filesystem.write")

        if "QA" in impact.revalidation_required:
            steps.append("6. Execute independent autonomous QA and verification via Agent #12")

        if not steps:
            steps.append("1. Direct metadata/documentation update; zero engineering revalidation required.")

        return ChangePlan(
            change_plan_id=f"PLAN-{change.change_id}",
            change_id=change.change_id,
            steps=steps,
            dependencies=["Agent #14 approval"] if impact.human_approval_required else [],
            revalidation_steps=impact.revalidation_required,
            qa_steps=["Agent #12 autonomous verification suite"],
            required_authorization=auth,
            required_approvals=approvals,
        )
