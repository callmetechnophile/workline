"""Tests for Rule versioning and Phase 10C validation cache invalidation."""

import pytest
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import knowledge_graph_service
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service


def test_rule_version_cache_invalidation():
    validation_service.set_rule_version("electrical_rules_v1")

    c1 = EngineeringConstraint(
        constraint_id="c_vout",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
    )
    validation_service.create_requirement(
        requirement_id="REQ-CACHE-1",
        project_id="rover_v2",
        description="3.3V output",
        constraints=[c1],
    )

    knowledge_graph_service.create_entity("ENT-CACHE-A", EntityType.COMPONENT, "TPS62130", "rover_v2")
    knowledge_graph_service.add_specification("S_C1", "ENT-CACHE-A", "output_voltage", "3.3 V", "ds.pdf", 1)

    # First validation run (creates cache entry with v1)
    val_v1 = validation_service.validate_candidate("REQ-CACHE-1", "ENT-CACHE-A")
    assert val_v1.rule_version == "electrical_rules_v1"

    # Bump rule version
    validation_service.set_rule_version("electrical_rules_v2")

    # Second validation run uses v2 key
    val_v2 = validation_service.validate_candidate("REQ-CACHE-1", "ENT-CACHE-A")
    assert val_v2.rule_version == "electrical_rules_v2"
