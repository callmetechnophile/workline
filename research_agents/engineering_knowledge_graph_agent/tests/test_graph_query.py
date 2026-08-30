"""
Unit tests for KnowledgeGraphService query and impact analysis (Sections 53–61).
"""

from datetime import datetime, timezone
import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.schemas import ProjectNode
from research_agents.engineering_knowledge_graph_agent.services.graph_query import KnowledgeGraphService


@pytest.mark.asyncio
async def test_graph_query_trace_and_impact():
    db = SurrealDBClient()
    service = KnowledgeGraphService(db)

    # Setup project
    await db.create_node("project", "proj_01", {
        "name": "SAR Drone",
        "owner_id": "user_001",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })

    trace = await service.get_requirement_trace("REQ-SAR-001", "proj_01", "user_001")
    assert trace.requirement_id == "REQ-SAR-001"
    assert len(trace.components) >= 1
    assert len(trace.validations) >= 1

    impact = await service.get_component_impact("500-0771-01", "proj_01", "user_001")
    assert impact.part_number == "500-0771-01"
    assert len(impact.affected_subsystems) >= 1
    assert len(impact.affected_bom_items) >= 1

    timeline = await service.get_project_timeline("proj_01", "user_001")
    assert len(timeline) >= 4
