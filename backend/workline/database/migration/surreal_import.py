"""SurrealDB data importer transforming normalized SQLite export into SurrealDB entities and graph relations."""

from typing import Any, Dict, List
from backend.workline.database.models import (
    CommentModel,
    GraphEdge,
    GraphNode,
    InvitationModel,
    ProjectModel,
    ProjectVersionModel,
    TeamMemberModel,
    TeamModel,
    WorkspaceBundleModel,
)
from backend.workline.database.repositories import (
    CollaborationRepository,
    GraphRepository,
    ProjectRepository,
)


async def import_data_to_surreal(
    data: Dict[str, List[Dict[str, Any]]],
    project_repo: ProjectRepository,
    collab_repo: CollaborationRepository,
    graph_repo: GraphRepository,
) -> Dict[str, int]:
    """
    Import normalized dataset into SurrealDB repositories and establish engineering graph relationships.
    Returns:
        Dictionary with imported counts per entity type.
    """
    counts = {
        "projects": 0,
        "teams": 0,
        "members": 0,
        "invitations": 0,
        "comments": 0,
        "bundles": 0,
        "versions": 0,
        "graph_nodes": 0,
        "graph_edges": 0,
    }

    # 1. Import Teams
    for t in data.get("teams", []):
        team = TeamModel(
            id=f"team:{t.get('uuid', t.get('id'))}",
            name=t.get("name", "Default Team"),
            uuid=str(t.get("uuid", t.get("id"))),
            created_at=t.get("created_at", ""),
        )
        await collab_repo.create_team(team)
        counts["teams"] += 1

    # 2. Import Members
    for m in data.get("members", []):
        member = TeamMemberModel(
            team_id=str(m.get("team_id", "")),
            user_id=str(m.get("user_id", "")),
            email=str(m.get("email", "")),
            role=str(m.get("role", "Engineer")),
            joined_at=str(m.get("joined_at", "")),
        )
        await collab_repo.add_member(member)
        counts["members"] += 1

    # 3. Import Invitations
    for inv in data.get("team_invitations", []):
        invitation = InvitationModel(
            team_id=str(inv.get("team_id", "")),
            email=str(inv.get("email", "")),
            role=str(inv.get("role", "Reviewer")),
            token_hash=str(inv.get("token_hash", "")),
            status=str(inv.get("status", "PENDING")),
            created_at=str(inv.get("created_at", "")),
        )
        await collab_repo.create_invitation(invitation)
        counts["invitations"] += 1

    # 4. Import Projects & Build Graph Relations
    for p in data.get("projects", []):
        p_name = p.get("name", "untitled")
        p_id = f"project:{p_name}"
        project = ProjectModel(
            id=p_id,
            name=p_name,
            display_name=p.get("name", "").replace("-", " ").title(),
            description=p.get("prompt", ""),
            domain="robotics",
            bom=p.get("bom", []) if isinstance(p.get("bom"), list) else [],
            power=p.get("power", {}) if isinstance(p.get("power"), dict) else {},
            dependencies=p.get("dependencies", {}) if isinstance(p.get("dependencies"), dict) else {},
            wiring=p.get("wiring", []) if isinstance(p.get("wiring"), list) else [],
            papers=p.get("papers", []) if isinstance(p.get("papers"), list) else [],
            gantt=p.get("gantt", []) if isinstance(p.get("gantt"), list) else [],
            version=p.get("version", 1),
            created_at=p.get("timestamp", ""),
            updated_at=p.get("timestamp", ""),
        )
        await project_repo.create_project(project)
        counts["projects"] += 1

        # Create Project Root Graph Node
        p_node = GraphNode(
            id=p_id,
            type="Project",
            label=project.display_name,
            data={"project_id": p_name},
        )
        await graph_repo.create_node(p_node)
        counts["graph_nodes"] += 1

        # Extract Components & Connect via SurrealDB Graph Edges (CONTAINS, USES)
        for idx, comp in enumerate(project.bom or []):
            comp_name = comp.get("name", f"Component_{idx}")
            comp_id = f"component:{p_name}_{comp_name.replace(' ', '_').lower()}"
            comp_node = GraphNode(
                id=comp_id,
                type="Component",
                label=comp_name,
                data={"project_id": p_name, **comp},
            )
            await graph_repo.create_node(comp_node)
            counts["graph_nodes"] += 1

            # Relation: Project -> CONTAINS -> Component
            edge = GraphEdge(
                id=f"edge:{p_id}_contains_{comp_id}",
                source=p_id,
                target=comp_id,
                relationship="CONTAINS",
                data={"project_id": p_name},
            )
            await graph_repo.create_edge(edge)
            counts["graph_edges"] += 1

    # 5. Import Versions
    for v in data.get("project_versions", []):
        version = ProjectVersionModel(
            project_id=str(v.get("project_id", "")),
            version_num=int(v.get("version_num", 1)),
            data=v.get("data", {}) if isinstance(v.get("data"), dict) else {},
            modified_by=str(v.get("modified_by", "System")),
            change_summary=str(v.get("change_summary", "")),
            created_at=str(v.get("created_at", "")),
        )
        await project_repo.save_version(version)
        counts["versions"] += 1

    # 6. Import Bundles
    for b in data.get("workspace_bundles", []):
        bundle = WorkspaceBundleModel(
            user_id=str(b.get("user_id", "")),
            name=str(b.get("name", "")),
            description=str(b.get("description", "")),
            bundle_blob=str(b.get("bundle_blob", "")),
            checksum=str(b.get("checksum", "")),
            bundle_size=int(b.get("bundle_size", 0)),
            field_count=int(b.get("field_count", 0)),
            version=int(b.get("version", 1)),
            saved_at=str(b.get("saved_at", "")),
        )
        await project_repo.save_bundle(bundle)
        counts["bundles"] += 1

    # 7. Import Comments
    for c in data.get("comments", []):
        comment = CommentModel(
            project_id=str(c.get("project_id", "")),
            section=str(c.get("section", "general")),
            author=str(c.get("author", "Engineer")),
            content=str(c.get("content", "")),
            timestamp=str(c.get("timestamp", "")),
        )
        await collab_repo.add_comment(comment)
        counts["comments"] += 1

    return counts
