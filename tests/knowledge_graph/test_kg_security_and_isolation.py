"""Tests for project/team isolation and no-hallucination factuality checks."""

import pytest
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import KnowledgeGraphService


def test_project_and_team_scoped_entity_search():
    service = KnowledgeGraphService()

    service.create_entity(
        entity_id="ENT-A",
        entity_type=EntityType.COMPONENT,
        canonical_name="TPS62130",
        project_id="project_A",
        team_id="team_alpha",
    )

    service.create_entity(
        entity_id="ENT-B",
        entity_type=EntityType.COMPONENT,
        canonical_name="TPS62130",
        project_id="project_B",
        team_id="team_beta",
    )

    # Search scoped to project_A
    res_a = service.search_entities("TPS62130", project_id="project_A")
    assert len(res_a) == 1
    assert res_a[0].entity_id == "ENT-A"

    # Search scoped to project_B
    res_b = service.search_entities("TPS62130", project_id="project_B")
    assert len(res_b) == 1
    assert res_b[0].entity_id == "ENT-B"


def test_no_hallucination_unsupported_facts_rejected():
    service = KnowledgeGraphService()
    service.create_entity(
        entity_id="ENT-REG",
        entity_type=EntityType.COMPONENT,
        canonical_name="TPS62130",
        project_id="rover_v2",
    )

    # Do not add Efficiency specification
    specs = service.get_specifications("ENT-REG")
    eff_spec = next((s for s in specs if "efficiency" in s.property.lower()), None)
    assert eff_spec is None  # Graph does not invent ungrounded facts
