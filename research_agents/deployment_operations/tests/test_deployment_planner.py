"""Tests for deployment planner."""
from research_agents.deployment_operations.schemas import SystemType
from research_agents.deployment_operations.services.deployment_planner import DeploymentPlanner


def test_create_deployment_plan_hybrid():
    planner = DeploymentPlanner()
    plan = planner.create_deployment_plan(
        project_id="PROJ-1",
        system_id="SYS-1",
        system_type=SystemType.HYBRID,
    )
    assert plan.system_id == "SYS-1"
    assert len(plan.steps) >= 4
    # All steps must have verification and rollback defined
    for step in plan.steps:
        assert step.verification_method is not None
        assert step.rollback_action is not None
