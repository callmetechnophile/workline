"""
Project lifecycle GraphQL mutations.
"""

import time
import strawberry
from strawberry.types import Info
from armourflow.graphql.inputs.project_inputs import CreateProjectInput
from armourflow.graphql.types.project import ProjectType


@strawberry.type
class ProjectMutations:
    @strawberry.mutation
    async def create_project(self, info: Info, input: CreateProjectInput) -> ProjectType:
        """Register a new engineering project in graph state."""
        ctx = info.context
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        doc = {
            "id": input.project_id,
            "title": input.title,
            "description": input.description or "",
            "created_at": now,
            "updated_at": now,
        }
        await ctx.db.create_node("project", input.project_id, doc)
        return ProjectType(
            id=input.project_id,
            title=input.title,
            description=input.description,
            created_at=now,
            updated_at=now,
        )
