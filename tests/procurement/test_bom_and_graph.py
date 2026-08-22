"""Unit and integration tests for BOM generation, SurrealDB graph nodes/edges, and human approval."""

import asyncio
import pytest
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.procurement.engine import ProcurementEngine
from backend.workline.procurement.models import (
    BOMStatus,
    ComponentRequirement,
)


def test_bom_generation_and_graph_persistence():
    """Test full BOM compilation, SurrealDB graph relationships (REQUIRES, CONTAINS, REFERENCES), and human approval."""
    async def _run():
        project_repo = ProjectRepository()
        graph_repo = GraphRepository()
        engine = ProcurementEngine(project_repo=project_repo, graph_repo=graph_repo)

        reqs = [
            ComponentRequirement(
                requirement_id="req_mcu",
                category="Microcontroller / Compute Unit",
                quantity=1,
                nominal_voltage=3.3,
            ),
            ComponentRequirement(
                requirement_id="req_reg",
                category="Power Management / Voltage Regulator",
                quantity=2,
                nominal_voltage=3.3,
                required_current_min_a=2.0,
            ),
            ComponentRequirement(
                requirement_id="req_env",
                category="Sensors & Environmental",
                quantity=1,
            ),
        ]

        bom, plan = await engine.generate_project_bom("autonomous-rover", reqs)

        assert bom.status == BOMStatus.READY_FOR_REVIEW
        assert len(bom.items) >= 3
        assert bom.total_component_cost > 0.0
        assert bom.estimated_total > 0.0

        # Verify SurrealDB Graph nodes and edges
        graph = await graph_repo.get_project_graph("autonomous-rover")
        node_types = [n.type for n in graph.nodes]
        edge_rels = [e.relationship for e in graph.edges]

        assert "ComponentRequirement" in node_types
        assert "BOM" in node_types
        assert "Component" in node_types
        assert "REQUIRES" in edge_rels
        assert "CONTAINS" in edge_rels
        assert "REFERENCES" in edge_rels

        # Test Human Approval
        approved_bom = await engine.approve_bom(bom.bom_id, approved_by="Chief Engineer")
        assert approved_bom is not None
        assert approved_bom.status == BOMStatus.APPROVED

    asyncio.run(_run())
