"""Tests for DAGEngine."""
from research_agents.project_execution_agent.schemas import PlanningTask
from research_agents.project_execution_agent.services.dag_engine import DAGEngine

def test_dag_linear():
    engine = DAGEngine()
    tasks = [
        PlanningTask(task_id="T1", work_package_id="WP1", title="Task 1", dependencies=[], estimated_hours=2.0),
        PlanningTask(task_id="T2", work_package_id="WP1", title="Task 2", dependencies=["T1"], estimated_hours=3.0),
        PlanningTask(task_id="T3", work_package_id="WP1", title="Task 3", dependencies=["T2"], estimated_hours=4.0),
    ]
    dag = engine.build_dag(tasks)
    assert not dag.has_cycle
    assert dag.topological_order == ["T1", "T2", "T3"]
    assert dag.critical_path == ["T1", "T2", "T3"]

def test_dag_cycle_detection():
    engine = DAGEngine()
    tasks = [
        PlanningTask(task_id="T1", work_package_id="WP1", title="Task 1", dependencies=["T2"], estimated_hours=2.0),
        PlanningTask(task_id="T2", work_package_id="WP1", title="Task 2", dependencies=["T1"], estimated_hours=3.0),
    ]
    dag = engine.build_dag(tasks)
    assert dag.has_cycle is True
    assert len(dag.topological_order) == 0
