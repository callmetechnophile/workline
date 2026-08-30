"""
Unit tests for KnowledgeGraphWriter service (Section 62).
"""

from datetime import datetime, timezone
import pytest
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.schemas import (
    ArchitectureNode,
    BOMItemNode,
    BOMNode,
    ComponentNode,
    EngineeringDecisionNode,
    ProjectNode,
    RequirementNode,
)
from research_agents.engineering_knowledge_graph_agent.services.audit_logger import GraphAuditLogger
from research_agents.engineering_knowledge_graph_agent.services.graph_writer import KnowledgeGraphWriter


@pytest.mark.asyncio
async def test_graph_writer_node_creation_and_linking():
    db = SurrealDBClient()
    audit = GraphAuditLogger()
    writer = KnowledgeGraphWriter(db, audit)

    proj = ProjectNode(
        id="project:proj_01",
        name="Test Drone",
        owner_id="user_123",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _, p_new = await writer.create_project(proj, owner_id="user_123")
    assert p_new is True

    req = RequirementNode(
        id="requirement:REQ-01",
        project_id="proj_01",
        title="Thermal Vision",
        description="15 FPS",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _, r_new = await writer.create_requirement(req)
    assert r_new is True

    comp = ComponentNode(
        id="component:500-0771-01",
        part_number="500-0771-01",
        manufacturer="Teledyne FLIR",
        category="Sensor",
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    _, c_new = await writer.create_component(comp, subsystem_id="ThermalImagingSubsystem")
    assert c_new is True

    assert len(audit.events) >= 3
