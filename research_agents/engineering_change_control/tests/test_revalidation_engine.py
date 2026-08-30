"""
Unit tests for ChangeRevalidationEngine (Sections 26 & 27).
"""

from research_agents.engineering_change_control.schemas import ChangeRequest, ImpactObject
from research_agents.engineering_change_control.services.revalidation_engine import ChangeRevalidationEngine


def test_revalidation_plan_creation():
    engine = ChangeRevalidationEngine()

    chg = ChangeRequest(
        change_id="C1",
        project_id="p1",
        change_type="COMPONENT_CHANGE",
        title="Replace sensor",
        description="Upgrade",
    )
    impact = ImpactObject(
        change_id="C1",
        revalidation_required=["BOM", "VALIDATION", "PLANNING", "IMPLEMENTATION", "QA"],
        human_approval_required=True,
    )

    plan = engine.create_revalidation_plan(chg, impact)
    assert len(plan.steps) >= 5
    assert any("Agent #8" in s for s in plan.steps)
    assert any("Agent #9" in s for s in plan.steps)
    assert any("Agent #11" in s for s in plan.steps)
    assert any("Agent #12" in s for s in plan.steps)
    assert "filesystem.write" in plan.required_authorization
