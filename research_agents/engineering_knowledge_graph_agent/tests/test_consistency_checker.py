"""
Unit tests for GraphConsistencyChecker service (Section 88).
"""

from datetime import datetime, timezone
import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.consistency_checker import GraphConsistencyChecker


@pytest.mark.asyncio
async def test_consistency_checker():
    db = SurrealDBClient()
    checker = GraphConsistencyChecker(db)

    # Clean project
    await db.create_node("project", "proj_01", {"name": "Test Project"})
    await db.create_node("requirement", "REQ-01", {"project_id": "proj_01", "title": "Req"})
    await db.relate_nodes("project:proj_01", "HAS_REQUIREMENT", "requirement:REQ-01")

    res = await checker.check_consistency("proj_01")
    assert res["status"] == "PASS"
    assert len(res["issues"]) == 0
