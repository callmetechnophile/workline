"""Tests for ScopeAssigner."""
from research_agents.project_execution_agent.schemas import PlanningTask
from research_agents.project_execution_agent.services.scope_assigner import ScopeAssigner

def test_scope_assignment():
    assigner = ScopeAssigner()
    tasks = [
        PlanningTask(task_id="T1", work_package_id="WP1", title="Test Runner Task", task_type="testing"),
        PlanningTask(task_id="T2", work_package_id="WP1", title="Code File Task", task_type="code", target_file="src/driver.py"),
    ]
    assigned = assigner.assign_scopes(tasks)
    assert "test_runner" in assigned[0].allowed_tools
    assert "filesystem" in assigned[1].allowed_tools
    assert "src/**" in assigned[1].allowed_paths
