"""
Unit tests for EvidenceCollector service (Sections 11–14).
"""

import pytest
from research_agents.engineering_copilot.services.evidence_collector import EvidenceCollector
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


@pytest.mark.asyncio
async def test_evidence_collector_gathers_evidence():
    db = SurrealDBClient()
    collector = EvidenceCollector(db)

    # Clean project setup
    await db.create_node("project", "proj_01", {"name": "Test Project", "owner_id": "user_001"})

    evidence = await collector.collect_project_evidence(
        project_id="proj_01",
        user_id="user_001",
        requirement_id="REQ-SAR-001",
        component_id="500-0771-01",
    )

    assert len(evidence) >= 2
    assert any(e.source_type == "requirement" for e in evidence)
    assert any(e.source_type == "bom" for e in evidence)
