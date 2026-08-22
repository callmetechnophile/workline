"""Tests for Specification extraction, unit normalization, numerical comparison, and conflict preservation."""

import pytest
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.normalizer import EntityNormalizer
from backend.workline.knowledge.graph.service import KnowledgeGraphService


def test_engineering_quantity_parsing():
    # Voltage
    v1 = EntityNormalizer.parse_quantity("3V3")
    assert v1 is not None and v1.normalized_value == 3.3 and v1.base_unit == "V"

    v2 = EntityNormalizer.parse_quantity("500mV")
    assert v2 is not None and v2.normalized_value == 0.5 and v2.base_unit == "V"

    # Current
    c1 = EntityNormalizer.parse_quantity("3A")
    assert c1 is not None and c1.normalized_value == 3.0 and c1.base_unit == "A"

    c2 = EntityNormalizer.parse_quantity("250mA")
    assert c2 is not None and c2.normalized_value == 0.25 and c2.base_unit == "A"

    # Resistance
    r1 = EntityNormalizer.parse_quantity("10k")
    assert r1 is not None and r1.normalized_value == 10000.0 and r1.base_unit == "Ω"


def test_numerical_requirement_evaluation():
    service = KnowledgeGraphService()
    service.create_entity(
        entity_id="ENT-TPS62130",
        entity_type=EntityType.COMPONENT,
        canonical_name="TPS62130",
        project_id="rover_v2",
    )

    # Add specifications
    service.add_specification(
        specification_id="SPEC-1",
        entity_id="ENT-TPS62130",
        property_name="output_voltage",
        value_str="3.3 V",
        source_document="datasheet.pdf",
        page=1,
    )
    service.add_specification(
        specification_id="SPEC-2",
        entity_id="ENT-TPS62130",
        property_name="output_current",
        value_str="3 A",
        source_document="datasheet.pdf",
        page=1,
    )

    # 1. Satisfied requirement (3.3V, >=2A)
    eval_pass = service.evaluate_requirement_candidate("ENT-TPS62130", required_voltage=3.3, min_current=2.0)
    assert eval_pass["satisfied"] is True

    # 2. Failed requirement (5.0V, >=2A)
    eval_fail_v = service.evaluate_requirement_candidate("ENT-TPS62130", required_voltage=5.0, min_current=2.0)
    assert eval_fail_v["satisfied"] is False

    # 3. Failed requirement (3.3V, >=5A)
    eval_fail_c = service.evaluate_requirement_candidate("ENT-TPS62130", required_voltage=3.3, min_current=5.0)
    assert eval_fail_c["satisfied"] is False


def test_conflicting_specifications_preserved():
    service = KnowledgeGraphService()
    service.create_entity(
        entity_id="ENT-TEST",
        entity_type=EntityType.COMPONENT,
        canonical_name="TestBuck",
        project_id="rover_v2",
    )

    # Document A claims 3A output
    service.add_specification(
        specification_id="SPEC-A",
        entity_id="ENT-TEST",
        property_name="Output Current",
        value_str="3 A",
        source_document="DocA_Datasheet.pdf",
        page=1,
    )

    # Document B claims 2A output
    service.add_specification(
        specification_id="SPEC-B",
        entity_id="ENT-TEST",
        property_name="Output Current",
        value_str="2 A",
        source_document="DocB_Paper.pdf",
        page=4,
    )

    # Verify both specifications are retained (neither was overwritten)
    specs = service.get_specifications("ENT-TEST")
    assert len(specs) == 2
    assert any(s.value == "3 A" for s in specs)
    assert any(s.value == "2 A" for s in specs)

    # Verify conflict was created
    conflicts = service.list_conflicts()
    assert len(conflicts) == 1
    assert conflicts[0].entity_id == "ENT-TEST"
    assert conflicts[0].property == "Output Current"
    assert "3 A" in conflicts[0].value_a
    assert "2 A" in conflicts[0].value_b
