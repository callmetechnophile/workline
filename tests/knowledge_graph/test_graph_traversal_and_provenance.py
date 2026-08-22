"""Tests for bounded graph traversal and evidence chain traceability."""

import pytest
from backend.workline.knowledge.graph.models import EntityType, RelationshipType
from backend.workline.knowledge.graph.service import KnowledgeGraphService


def test_bounded_graph_traversal_and_decision_trace():
    service = KnowledgeGraphService()

    # 1. Entities: Requirement -> Decision -> Component -> Datasheet -> Specification
    service.create_entity("REQ-POWER", EntityType.REQUIREMENT, "3.3V System Power", "rover_v2")
    service.create_entity("DEC-REGULATOR", EntityType.DECISION, "Select Synchronous Buck", "rover_v2")
    service.create_entity("ENT-TPS62130", EntityType.COMPONENT, "TPS62130", "rover_v2", manufacturer="Texas Instruments")
    service.create_entity("DOC-TPS62130", EntityType.DOCUMENT, "TPS62130.pdf", "rover_v2")

    # 2. Graph Edges
    service.add_relationship("R1", "rover_v2", "REQ-POWER", RelationshipType.SATISFIED_BY, "DEC-REGULATOR")
    service.add_relationship("R2", "rover_v2", "DEC-REGULATOR", RelationshipType.SELECTS, "ENT-TPS62130")
    service.add_relationship("R3", "rover_v2", "ENT-TPS62130", RelationshipType.HAS_DATASHEET, "DOC-TPS62130")

    # 3. Specification with provenance
    service.add_specification(
        specification_id="SPEC-1",
        entity_id="ENT-TPS62130",
        property_name="Output Current",
        value_str="3 A",
        source_document="TPS62130.pdf",
        page=1,
        section="Features",
        confidence=1.0,
    )

    # 4. Traversal query on component
    graph_res = service.get_related("ENT-TPS62130", max_depth=2)
    assert graph_res["entity"]["canonical_name"] == "TPS62130"
    assert len(graph_res["relationships"]) == 2
    assert len(graph_res["specifications"]) == 1
    assert graph_res["specifications"][0]["property"] == "Output Current"
    assert graph_res["specifications"][0]["source_document"] == "TPS62130.pdf"
