"""Tests for ProjectExecutionAgent Pydantic schemas."""
from research_agents.project_execution_agent.schemas import (
    DependencyDAG,
    ImplementationPlan,
    PlanningTask,
    ProjectExecutionAgentInput,
    ProjectExecutionAgentOutput,
    WorkPackage,
)

def test_task_schema():
    task = PlanningTask(
        task_id="TASK-001",
        work_package_id="WP-001",
        title="Setup Environment",
        task_type="configuration",
        priority="high",
        dependencies=[],
        allowed_tools=["filesystem"],
    )
    assert task.task_id == "TASK-001"
    assert task.priority == "high"
    assert task.status == "pending"

def test_work_package_schema():
    wp = WorkPackage(
        work_package_id="WP-001",
        title="Core Setup",
        phase="DESIGN",
        estimated_hours=4.0,
    )
    assert wp.work_package_id == "WP-001"
    assert wp.phase == "DESIGN"

def test_plan_schema():
    plan = ImplementationPlan(
        project_id="proj_01",
        title="SAR Drone",
        engineering_domain="Robotics",
    )
    assert plan.project_id == "proj_01"
    assert plan.execution_readiness is True
