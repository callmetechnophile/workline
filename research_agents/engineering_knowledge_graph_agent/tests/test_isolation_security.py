"""
Security tests for multi-tenant project isolation (Sections 6, 67, 68).
"""

from datetime import datetime, timezone
import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService


@pytest.mark.asyncio
async def test_multi_user_isolation_blocks_cross_project_access():
    db = SurrealDBClient()
    service = KnowledgeGraphService(db)

    # Project A owned by User A
    await db.create_node("project", "proj_A", {
        "name": "Project A",
        "owner_id": "user_A",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # User A accesses Project A -> OK
    graph_a = await service.get_project_graph("proj_A", user_id="user_A")
    assert graph_a["project_id"] == "proj_A"

    # User B attempts to access Project A -> PermissionError (ACCESS_DENIED)
    with pytest.raises(PermissionError, match="ACCESS_DENIED"):
        await service.get_project_graph("proj_A", user_id="user_B")
