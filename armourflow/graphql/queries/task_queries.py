"""
Task lifecycle and history GraphQL query resolvers.
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from armourflow.graphql.types.task import FabricTaskType, TaskContextType, task_to_graphql_type
from armourflow.graphql.errors import create_graphql_error, GraphQLErrorCode


@strawberry.type
class TaskQueries:
    @strawberry.field
    def task(self, info: Info, id: str) -> Optional[FabricTaskType]:
        """Retrieve task state, execution results, and errors by task ID."""
        ctx = info.context
        task = ctx.fabric.get_task(id)
        if not task:
            raise create_graphql_error(
                f"Task '{id}' not found in Control Fabric.",
                code=GraphQLErrorCode.NOT_FOUND,
                details={"task_id": id},
            )

        # Enforce tenant isolation
        if ctx.project_id != "default" and task.context.project_id != ctx.project_id:
            raise create_graphql_error(
                f"Access denied to task '{id}' across tenant boundaries.",
                code=GraphQLErrorCode.AUTHORIZATION_ERROR,
                details={"project_id": ctx.project_id, "task_project_id": task.context.project_id},
            )

        return task_to_graphql_type(task)

    @strawberry.field
    def tasks(
        self,
        info: Info,
        project_id: Optional[str] = None,
        limit: int = 50,
    ) -> List[FabricTaskType]:
        """List tasks scoped to a project with limit protection."""
        ctx = info.context
        pid = project_id or ctx.project_id
        safe_limit = min(max(1, limit), 100)
        tasks = ctx.fabric.list_tasks(pid)[:safe_limit]

        return [task_to_graphql_type(t) for t in tasks]
