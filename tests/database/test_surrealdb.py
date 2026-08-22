"""Unit and integration tests for SurrealDB repositories and engineering knowledge graph."""

import asyncio
from backend.workline.database.models import (
    CommentModel,
    GraphEdge,
    GraphNode,
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
from backend.workline.database.surrealdb import SurrealDBManager


def test_project_repository_crud():
    """Test 3-6: Project creation, retrieval, update, and deletion in SurrealDB repo."""
    async def _run():
        mgr = SurrealDBManager()
        repo = ProjectRepository(mgr)

        # 1. Create project
        proj = ProjectModel(
            id="project:solar_rover",
            name="solar_rover",
            display_name="Solar Rover",
            description="Autonomous solar rover",
            domain="robotics",
            bom=[{"name": "ESP32-S3", "quantity": 1}],
        )
        saved = await repo.create_project(proj)
        assert saved.id == "project:solar_rover"

        # 2. Retrieve project
        retrieved = await repo.get_project("solar_rover")
        assert retrieved is not None
        assert retrieved.name == "solar_rover"
        assert retrieved.display_name == "Solar Rover"

        # 3. Update project
        updated = await repo.update_project("solar_rover", {"description": "Updated solar rover"})
        assert updated is not None
        assert updated.description == "Updated solar rover"

        # 4. List projects
        all_projects = await repo.list_projects()
        assert len(all_projects) >= 1
        assert any(p.name == "solar_rover" for p in all_projects)

        # 5. Delete project
        deleted = await repo.delete_project("solar_rover")
        assert deleted is True
        assert await repo.get_project("solar_rover") is None

    asyncio.run(_run())


def test_project_versions_and_bundles():
    """Test 7: Project versions and compressed workspace bundles persistence."""
    async def _run():
        mgr = SurrealDBManager()
        repo = ProjectRepository(mgr)

        # Save version
        ver = ProjectVersionModel(
            project_id="solar_rover",
            version_num=1,
            data={"bom": []},
            modified_by="Engineer",
            change_summary="Initial design",
        )
        await repo.save_version(ver)
        versions = await repo.get_versions("solar_rover")
        assert len(versions) == 1
        assert versions[0].version_num == 1

        # Save bundle
        bundle = WorkspaceBundleModel(
            user_id="user_123",
            name="Solar Rover Bundle",
            description="Release package",
            bundle_blob="H4sIC...",
            checksum="abc12345",
            bundle_size=1024,
            field_count=10,
            version=1,
        )
        await repo.save_bundle(bundle)
        bundles = await repo.get_bundles("user_123")
        assert len(bundles) == 1
        assert bundles[0].name == "Solar Rover Bundle"

    asyncio.run(_run())


def test_graph_repository_traversal():
    """Test 8-9: Engineering knowledge graph relations, record links, and traversal."""
    async def _run():
        mgr = SurrealDBManager()
        repo = GraphRepository(mgr)

        # 1. Create nodes
        p_node = GraphNode(id="project:rover", type="Project", label="Autonomous Rover", data={"project_id": "rover"})
        mcu_node = GraphNode(id="component:esp32", type="Component", label="ESP32-S3", data={"project_id": "rover"})
        sensor_node = GraphNode(id="component:imu", type="Component", label="MPU6050", data={"project_id": "rover"})

        await repo.create_node(p_node)
        await repo.create_node(mcu_node)
        await repo.create_node(sensor_node)

        # 2. Create edges (CONTAINS, CONNECTS_TO)
        e1 = GraphEdge(id="edge:rover_esp32", source="project:rover", target="component:esp32", relationship="CONTAINS")
        e2 = GraphEdge(id="edge:esp32_imu", source="component:esp32", target="component:imu", relationship="CONNECTS_TO")

        await repo.create_edge(e1)
        await repo.create_edge(e2)

        # 3. Project graph traversal
        graph = await repo.get_project_graph("rover")
        assert len(graph.nodes) >= 3
        assert len(graph.edges) >= 2

        # 4. Component 1-hop subgraph traversal
        mcu_graph = await repo.get_component_graph("component:esp32")
        assert len(mcu_graph.nodes) >= 2
        assert any(e.relationship == "CONNECTS_TO" for e in mcu_graph.edges)

        # 5. Path query
        path_graph = await repo.get_path_graph("component:esp32", "component:imu")
        assert len(path_graph.edges) == 1

    asyncio.run(_run())


def test_collaboration_repository():
    """Test team spaces, member rosters, and comment threads in SurrealDB."""
    async def _run():
        mgr = SurrealDBManager()
        repo = CollaborationRepository(mgr)

        # Create team
        team = TeamModel(name="Hardware Robotics", uuid="123456")
        await repo.create_team(team)

        retrieved_team = await repo.get_team_by_uuid("123456")
        assert retrieved_team is not None
        assert retrieved_team.name == "Hardware Robotics"

        # Add member
        member = TeamMemberModel(team_id="123456", user_id="lead_eng", email="lead@workline.dev", role="Owner")
        await repo.add_member(member)

        members = await repo.get_members("123456")
        assert len(members) == 1
        assert members[0].email == "lead@workline.dev"

        # Add comment
        comment = CommentModel(project_id="rover", section="bom", author="lead@workline.dev", content="Select low-ESR capacitors")
        await repo.add_comment(comment)

        comments = await repo.get_comments("rover")
        assert len(comments) == 1
        assert comments[0].content == "Select low-ESR capacitors"

    asyncio.run(_run())
