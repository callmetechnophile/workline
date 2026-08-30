"""
Unit tests for ExecutionRepository persistence interface (Section 84).
"""

import pytest
from research_agents.engineering_execution_agent.repository import InMemoryExecutionRepository
from research_agents.engineering_execution_agent.schemas import (
    DelegationObject,
    EngineeringExecutionAgentOutput,
    ExecutionAuditItem,
    ExecutionGraph,
    ToolCallRecord,
)


@pytest.mark.asyncio
async def test_execution_repository_all_methods():
    repo = InMemoryExecutionRepository()
    exec_id = "exec_test_001"

    # 1. Save tool call
    await repo.save_tool_call(
        ToolCallRecord(
            tool_call_id="CALL-01",
            task_id="TASK-01",
            tool="filesystem",
            operation="create",
            resource="test.py",
            status="success",
        ),
        exec_id,
    )

    # 2. Save audit event
    await repo.save_audit_event(
        ExecutionAuditItem(
            audit_id="AUD-01",
            timestamp="2026-08-30T12:00:00Z",
            project_id="proj_01",
            execution_id=exec_id,
            task_id="TASK-01",
            agent_id="EngineeringExecutionAgent",
            authorization_id="AUTH-01",
            tool="filesystem",
            operation="create",
            resource="test.py",
            status="SUCCESS",
        ),
        exec_id,
    )

    # 3. Save graph
    await repo.save_execution_graph(ExecutionGraph(nodes=[], edges=[]), exec_id)

    # 4. Save output
    output = EngineeringExecutionAgentOutput(
        status="success",
        execution_id=exec_id,
        project_id="proj_01",
        authorization_id="AUTH-01",
    )
    saved_id = await repo.save_execution(output)
    assert saved_id == exec_id

    retrieved = await repo.get_execution(exec_id)
    assert retrieved is not None
    assert retrieved.status == "success"
