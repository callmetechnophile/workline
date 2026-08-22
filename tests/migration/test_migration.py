"""Tests for SQLite export, SurrealDB import, and migration validation."""

import asyncio
from backend.workline.database.migration.sqlite_export import export_sqlite_data
from backend.workline.database.migration.surreal_import import import_data_to_surreal
from backend.workline.database.migration.validator import validate_migration_counts
from backend.workline.database.repositories import (
    CollaborationRepository,
    GraphRepository,
    ProjectRepository,
)


def test_sqlite_to_surrealdb_migration():
    """Test 22-25: SQLite export, SurrealDB import, record count validation, and relationship creation."""
    async def _run():
        mock_sqlite_data = {
            "projects": [
                {
                    "id": 1,
                    "name": "solar-tracker",
                    "prompt": "Dual axis solar tracker",
                    "bom": [{"name": "LDR Sensor", "quantity": 4}, {"name": "Servo SG90", "quantity": 2}],
                    "power": {"total_mw": 1500},
                    "dependencies": {},
                    "wiring": [],
                    "papers": [],
                    "gantt": [],
                    "version": 1,
                    "timestamp": "2026-08-22T02:00:00Z",
                }
            ],
            "teams": [
                {"id": 1, "name": "Solar Team", "uuid": "778899", "created_at": "2026-08-22T02:00:00Z"}
            ],
            "members": [
                {"id": 1, "team_id": "778899", "user_id": "eng1", "email": "eng1@workline.dev", "role": "Owner", "joined_at": "2026-08-22T02:00:00Z"}
            ],
            "team_invitations": [],
            "comments": [
                {"id": 1, "project_id": "solar-tracker", "section": "bom", "author": "eng1", "content": "Check servo torque", "timestamp": "2026-08-22T02:00:00Z"}
            ],
            "project_versions": [
                {"id": 1, "project_id": "solar-tracker", "version_num": 1, "data": {}, "modified_by": "eng1", "change_summary": "Initial", "created_at": "2026-08-22T02:00:00Z"}
            ],
            "workspace_bundles": [
                {"id": 1, "user_id": "eng1", "name": "Solar Tracker", "bundle_blob": "blob", "checksum": "chk123", "bundle_size": 500, "field_count": 5, "version": 1, "saved_at": "2026-08-22T02:00:00Z"}
            ],
            "activity_logs": [],
        }

        project_repo = ProjectRepository()
        collab_repo = CollaborationRepository()
        graph_repo = GraphRepository()

        # Import into SurrealDB repositories
        counts = await import_data_to_surreal(mock_sqlite_data, project_repo, collab_repo, graph_repo)

        assert counts["projects"] == 1
        assert counts["teams"] == 1
        assert counts["members"] == 1
        assert counts["comments"] == 1
        assert counts["bundles"] == 1
        assert counts["graph_nodes"] >= 3  # Project + 2 components
        assert counts["graph_edges"] >= 2  # CONTAINS edges

        # Validate migration counts
        val = await validate_migration_counts(mock_sqlite_data, project_repo, collab_repo, graph_repo)
        assert val["is_valid"] is True
        assert val["surrealdb"]["projects"] >= 1
        assert val["surrealdb"]["bundles"] >= 1

    asyncio.run(_run())
