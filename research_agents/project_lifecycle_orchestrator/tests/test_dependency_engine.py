"""
Unit tests for DependencyEngine and parallel task detection (Sections 16 & 39).
"""

from research_agents.project_lifecycle_orchestrator.services.dependency_engine import DependencyEngine


def test_dependency_engine_parallel_and_blocked():
    engine = DependencyEngine()

    tasks = [
        {"task_id": "T1", "dependencies": []},
        {"task_id": "T2", "dependencies": []},
        {"task_id": "T3", "dependencies": ["T1", "T2"]},
    ]

    # Initially T1 and T2 are ready in parallel; T3 is blocked
    res1 = engine.evaluate_dependencies(tasks, completed_task_ids=set())
    assert len(res1["ready_tasks"]) == 2
    assert len(res1["blocked_tasks"]) == 1
    assert res1["can_parallelize"] is True

    # After T1 and T2 complete, T3 is ready
    res2 = engine.evaluate_dependencies(tasks, completed_task_ids={"T1", "T2"})
    assert len(res2["ready_tasks"]) == 1
    assert res2["ready_tasks"][0]["task_id"] == "T3"
