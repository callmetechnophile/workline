"""
Unit tests for ExecutionGraphBuilder (Section 54).
"""

from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    EngineeringExecutionContext,
    ToolCallRecord,
)
from research_agents.engineering_execution_agent.services.execution_graph import ExecutionGraphBuilder


def test_execution_graph_construction():
    builder = ExecutionGraphBuilder()
    context = EngineeringExecutionContext(user_id="user_123", project_id="proj_01", parent_agent_id="Orchestrator")
    auth = AuthorizedExecution(authorization_id="AUTH-01")

    completed = [{"task_id": "TASK-001", "title": "Sensor Task", "status": "completed"}]
    failed = []
    tool_calls = [
        ToolCallRecord(
            tool_call_id="CALL-01",
            task_id="TASK-001",
            tool="filesystem",
            operation="create",
            resource="firmware/sensor.py",
            status="success",
            armoriq_receipt_id="RCPT-01",
        )
    ]

    graph = builder.build_graph(context, auth, completed, failed, tool_calls)

    assert len(graph.nodes) >= 5
    assert len(graph.edges) >= 4

    node_types = [n.type for n in graph.nodes]
    assert "user" in node_types
    assert "agent" in node_types
    assert "authorization" in node_types
    assert "task" in node_types
    assert "tool" in node_types
    assert "receipt" in node_types
