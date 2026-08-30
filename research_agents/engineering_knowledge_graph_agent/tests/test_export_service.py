"""
Unit tests for GraphExporter service (Sections 72 & 77).
"""

from pathlib import Path
import tempfile
import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.export_service import GraphExporter


@pytest.mark.asyncio
async def test_graph_export_service():
    db = SurrealDBClient()
    exporter = GraphExporter(db)

    await db.create_node("project", "proj_01", {"name": "Test Project"})
    await db.create_node("requirement", "REQ-01", {"project_id": "proj_01", "title": "Req"})
    await db.relate_nodes("project:proj_01", "HAS_REQUIREMENT", "requirement:REQ-01")

    with tempfile.TemporaryDirectory() as tmp_dir:
        files = exporter.export_to_directory("proj_01", tmp_dir)
        assert len(files) == 2

        dir_p = Path(tmp_dir)
        assert (dir_p / "project_graph.json").exists()
        assert (dir_p / "cytoscape_graph.json").exists()
