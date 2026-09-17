"""
Project graph state and exploration GraphQL query resolvers.
"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from armourflow.graphql.types.project import (
    ProjectType,
    ProjectStatusType,
    EngineeringGraph,
    GraphNode,
    GraphEdge,
)


@strawberry.type
class ProjectQueries:
    @strawberry.field
    async def projects(self, info: Info, limit: int = 50) -> List[ProjectType]:
        """List engineering projects stored in the graph database."""
        ctx = info.context
        safe_limit = min(max(1, limit), 100)
        records = await ctx.db.list_by_table("project")
        if not records:
            return [
                ProjectType(
                    id="default",
                    title="Default Engineering Project",
                    description="Standard engineering workspace project",
                    created_at="system_init",
                    updated_at="system_init",
                )
            ]

        return [
            ProjectType(
                id=r.get("id", "UNKNOWN"),
                title=r.get("title", "Untitled Project"),
                description=r.get("description"),
                created_at=r.get("created_at"),
                updated_at=r.get("updated_at"),
            )
            for r in records[:safe_limit]
        ]

    @strawberry.field
    def project_status(self, info: Info, id: str) -> ProjectStatusType:
        """Inspect task completion metrics and readiness status for a project."""
        ctx = info.context
        tasks = ctx.fabric.list_tasks(id)
        completed = sum(1 for t in tasks if t.state.value == "COMPLETED")
        failed = sum(1 for t in tasks if t.state.value == "FAILED")

        return ProjectStatusType(
            project_id=id,
            associated_tasks=len(tasks),
            completed_tasks=completed,
            failed_tasks=failed,
            readiness_verdict="ACTIVE" if tasks else "INITIALIZED",
        )

    @strawberry.field
    async def engineering_graph(self, info: Info, project_id: str) -> EngineeringGraph:
        """Inspect engineering knowledge graph nodes and relationships for a project."""
        ctx = info.context
        raw_nodes = await ctx.db.list_by_table("node")
        raw_edges = await ctx.db.list_by_table("rel")

        nodes = [
            GraphNode(id=n.get("id", "node"), table=n.get("table", "node"), data=n)
            for n in raw_nodes
        ]
        edges = [
            GraphEdge(
                source=e.get("in", ""),
                relationship=e.get("rel", "relates_to"),
                target=e.get("out", ""),
            )
            for e in raw_edges
        ]

        return EngineeringGraph(
            project_id=project_id,
            nodes=nodes,
            edges=edges,
        )
