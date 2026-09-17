"""
Task submission, execution, and cancellation GraphQL mutations.
Routes strictly through the Unified Agent Control Fabric.
"""

from typing import Optional
import strawberry
from strawberry.types import Info
from armourflow.graphql.inputs.task_inputs import CreateTaskInput, RunCapabilityTaskInput
from armourflow.graphql.types.task import FabricTaskType, TaskContextType, task_to_graphql_type
from armourflow.graphql.errors import create_graphql_error, GraphQLErrorCode


@strawberry.type
class TaskMutations:
    @strawberry.mutation
    async def create_task(self, info: Info, input: CreateTaskInput) -> FabricTaskType:
        """
        Submit a task to the Agent Control Fabric.
        Routes either to target_agent_id or resolves dynamically via target_capability.
        """
        ctx = info.context
        if not input.agent_id and not input.capability:
            raise create_graphql_error(
                "Either agentId or capability must be specified to route task.",
                code=GraphQLErrorCode.VALIDATION_ERROR,
            )

        payload = input.payload if isinstance(input.payload, dict) else {}

        task = await ctx.fabric.submit_task(
            payload=payload,
            target_agent_id=input.agent_id,
            target_capability=input.capability,
            project_id=input.project_id or ctx.project_id,
            user_id=ctx.user_id,
        )

        return task_to_graphql_type(task)

    @strawberry.mutation
    async def run_capability_task(self, info: Info, input: RunCapabilityTaskInput) -> FabricTaskType:
        """
        Convenience mutation to dispatch tasks purely based on declared capability name.
        Control Fabric automatically resolves the providing agent without client N*N coupling.
        """
        ctx = info.context
        payload = input.payload if isinstance(input.payload, dict) else {}

        task = await ctx.fabric.submit_task(
            payload=payload,
            target_capability=input.capability,
            project_id=input.project_id or ctx.project_id,
            user_id=ctx.user_id,
        )

        return task_to_graphql_type(task)

    @strawberry.mutation
    def cancel_task(self, info: Info, task_id: str) -> bool:
        """Request cancellation of a running or queued fabric task."""
        ctx = info.context
        return ctx.fabric.cancel_task(task_id)
