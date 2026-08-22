"""Data migration validation engine for comparing source SQLite vs target SurrealDB records."""

from typing import Any, Dict
from backend.workline.database.repositories import (
    CollaborationRepository,
    GraphRepository,
    ProjectRepository,
)


async def validate_migration_counts(
    sqlite_data: Dict[str, Any],
    project_repo: ProjectRepository,
    collab_repo: CollaborationRepository,
    graph_repo: GraphRepository,
) -> Dict[str, Any]:
    """
    Validate record counts between SQLite source and SurrealDB destination.
    """
    surreal_projects = await project_repo.list_projects()
    surreal_bundles = await project_repo.get_bundles()

    sqlite_project_count = len(sqlite_data.get("projects", []))
    sqlite_team_count = len(sqlite_data.get("teams", []))
    sqlite_member_count = len(sqlite_data.get("members", []))
    sqlite_bundle_count = len(sqlite_data.get("workspace_bundles", []))

    surreal_project_count = len(surreal_projects)
    surreal_bundle_count = len(surreal_bundles)

    total_graph_nodes = len(graph_repo._nodes)
    total_graph_edges = len(graph_repo._edges)

    is_valid = (
        surreal_project_count >= sqlite_project_count
        and surreal_bundle_count >= sqlite_bundle_count
    )

    return {
        "is_valid": is_valid,
        "sqlite": {
            "projects": sqlite_project_count,
            "teams": sqlite_team_count,
            "members": sqlite_member_count,
            "bundles": sqlite_bundle_count,
        },
        "surrealdb": {
            "projects": surreal_project_count,
            "bundles": surreal_bundle_count,
            "graph_nodes": total_graph_nodes,
            "graph_edges": total_graph_edges,
        },
    }
