"""Tests for PlanRepository."""
import pytest
from research_agents.project_execution_agent.repository.plan_repository import PlanRepository
from research_agents.project_execution_agent.schemas import ImplementationPlan, WorkPackage

@pytest.mark.asyncio
async def test_plan_repository_in_memory():
    repo = PlanRepository()
    plan = ImplementationPlan(
        plan_id="PLAN-TEST-001",
        project_id="proj_01",
        title="SAR Drone",
        engineering_domain="Robotics",
        work_packages=[WorkPackage(work_package_id="WP-1", title="Setup")],
    )
    saved = await repo.save_plan(plan)
    assert saved.plan_id == "PLAN-TEST-001"
    retrieved = await repo.get_plan("PLAN-TEST-001")
    assert retrieved is not None
    assert retrieved.title == "SAR Drone"
