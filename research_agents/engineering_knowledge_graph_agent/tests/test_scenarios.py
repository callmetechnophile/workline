"""
Integration test scenarios mandated by specification (Sections 94–101).
"""

from datetime import datetime, timezone
import pytest

from research_agents.engineering_knowledge_graph_agent.agent import EngineeringKnowledgeGraphAgent
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.providers.mock_provider import MockGraphProvider
from research_agents.engineering_knowledge_graph_agent.schemas import (
    EngineeringDecisionNode,
    EngineeringKnowledgeGraphInput,
)
from research_agents.engineering_knowledge_graph_agent.services.audit_logger import GraphAuditLogger
from research_agents.engineering_knowledge_graph_agent.services.graph_writer import KnowledgeGraphWriter


@pytest.mark.asyncio
async def test_scenario_94_complete_traceability():
    """Section 94: Complete Traceability Chain."""
    agent = EngineeringKnowledgeGraphAgent(reasoning_provider=MockGraphProvider())
    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "SAR Drone", "project_id": "proj_94"},
        requirements=[{"requirement_id": "REQ-SAR-001", "description": "Thermal Vision 15 FPS"}],
        verification_qa={"verdict": "VERIFIED"},
    )
    out = await agent.run(input_data)
    assert out.status == "success"

    trace = await agent.query_service.get_requirement_trace("REQ-SAR-001", "proj_94", "user_001")
    assert trace.requirement_id == "REQ-SAR-001"
    assert len(trace.decisions) >= 1
    assert len(trace.architectures) >= 1
    assert len(trace.subsystems) >= 1
    assert len(trace.components) >= 1
    assert len(trace.boms) >= 1
    assert len(trace.tasks) >= 1
    assert len(trace.tests) >= 1
    assert len(trace.validations) >= 1


@pytest.mark.asyncio
async def test_scenario_95_component_impact():
    """Section 95: Component impact returns subsystems, tasks, tests, and requirements."""
    agent = EngineeringKnowledgeGraphAgent(reasoning_provider=MockGraphProvider())
    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "SAR Drone", "project_id": "proj_95"},
        bom={"items": [{"component_id": "500-0771-01", "name": "FLIR Lepton"}]},
        verification_qa={"verdict": "VERIFIED"},
    )
    await agent.run(input_data)

    impact = await agent.query_service.get_component_impact("500-0771-01", "proj_95", "user_001")
    assert impact.part_number == "500-0771-01"
    assert len(impact.affected_subsystems) >= 1
    assert len(impact.affected_bom_items) >= 1
    assert len(impact.affected_tasks) >= 1


@pytest.mark.asyncio
async def test_scenario_97_duplicate_ingestion_prevention():
    """Section 97: Ingesting the same BOM twice produces zero duplicate component/BOM nodes."""
    db = SurrealDBClient()
    agent = EngineeringKnowledgeGraphAgent(db_client=db, reasoning_provider=MockGraphProvider())

    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "SAR Drone", "project_id": "proj_97"},
        bom={"items": [{"component_id": "500-0771-01", "name": "FLIR Lepton"}]},
        verification_qa={"verdict": "VERIFIED"},
    )

    # First ingestion
    out1 = await agent.run(input_data)
    nodes_1 = len(db.in_memory.nodes)

    # Second ingestion with same data
    out2 = await agent.run(input_data)
    nodes_2 = len(db.in_memory.nodes)

    assert nodes_1 == nodes_2  # Zero duplicate nodes created


@pytest.mark.asyncio
async def test_scenario_98_database_failure():
    """Section 98: Simulated database outage returns DATABASE_UNAVAILABLE."""
    db_fail = SurrealDBClient(simulate_failure=True)
    agent = EngineeringKnowledgeGraphAgent(db_client=db_fail, reasoning_provider=MockGraphProvider())

    input_data = EngineeringKnowledgeGraphInput(
        project={"title": "SAR Drone", "project_id": "proj_98"},
    )

    with pytest.raises(RuntimeError, match="DATABASE_UNAVAILABLE"):
        await agent.run(input_data)


@pytest.mark.asyncio
async def test_scenario_99_decision_versioning():
    """Section 99: Historical decision preserved with SUPERSEDES link."""
    db = SurrealDBClient()
    writer = KnowledgeGraphWriter(db, GraphAuditLogger())

    # Decision V1
    dec1 = EngineeringDecisionNode(
        id="engineering_decision:DEC-01",
        project_id="proj_99",
        title="Original Camera Decision",
        decision="Use 9 FPS Lepton 2.5",
        reasoning="Lower cost",
        selected_option="Lepton 2.5",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    await writer.create_decision(dec1)

    # Decision V2 supersedes V1
    dec2 = EngineeringDecisionNode(
        id="engineering_decision:DEC-02",
        project_id="proj_99",
        title="Upgraded Camera Decision",
        decision="Use 15 FPS Lepton 3.5",
        reasoning="Required for fast SAR flight",
        selected_option="Lepton 3.5",
        created_at=datetime.now(timezone.utc).isoformat(),
        supersedes="DEC-01",
    )
    await writer.create_decision(dec2)

    # Verify both exist and are linked
    assert await db.get_node("engineering_decision:DEC-01") is not None
    assert await db.get_node("engineering_decision:DEC-02") is not None
    outbound = await db.get_outbound("engineering_decision:DEC-01", "SUPERSEDES")
    assert len(outbound) == 1
    assert outbound[0].target_id == "engineering_decision:DEC-02"
