"""
FabricTask and execution result GraphQL types.
"""

from typing import Any, Optional
import strawberry
from strawberry.scalars import JSON


@strawberry.type
class TaskContextType:
    project_id: str
    user_id: str
    request_id: str
    workflow_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None


@strawberry.type
class FabricTaskType:
    task_id: str
    target_agent_id: Optional[str] = None
    target_capability: Optional[str] = None
    state: str
    created_at: str
    updated_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    payload: JSON
    result: Optional[JSON] = None
    error: Optional[str] = None
    context: TaskContextType


def task_to_graphql_type(task: Any) -> FabricTaskType:
    """Helper to convert internal FabricTask model to GraphQL FabricTaskType."""
    ctx = task.context
    return FabricTaskType(
        task_id=task.task_id,
        target_agent_id=task.target_agent_id,
        target_capability=task.target_capability,
        state=task.state.value if hasattr(task.state, "value") else str(task.state),
        created_at=str(task.created_at),
        updated_at=str(task.updated_at) if getattr(task, "updated_at", None) is not None else str(task.created_at),
        started_at=str(task.started_at) if getattr(task, "started_at", None) is not None else None,
        completed_at=str(task.completed_at) if getattr(task, "completed_at", None) is not None else None,
        payload=task.payload or {},
        result=task.result,
        error=task.error,
        context=TaskContextType(
            project_id=ctx.project_id,
            user_id=ctx.user_id,
            request_id=getattr(ctx, "request_id", ""),
            workflow_id=getattr(ctx, "workflow_id", None),
            session_id=getattr(ctx, "session_id", None),
            correlation_id=getattr(ctx, "correlation_id", None) or getattr(ctx, "request_id", None),
        ),
    )
