"""Tests for deterministic candidate validation outcomes: PASS, FAIL, UNKNOWN, CONFLICT."""

import pytest
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import knowledge_graph_service
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service


@pytest.fixture(autouse=True)
def setup_validation_fixture():
    # 1. Requirement
    c1 = EngineeringConstraint(
        constraint_id="c_vout",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
    )
    c2 = EngineeringConstraint(
        constraint_id="c_iout",
        property="output_current",
        operator=ConstraintOperator.GTE,
        required_value="2A",
        required_unit="A",
        normalized_value=2.0,
    )
    validation_service.create_requirement(
        requirement_id="REQ-EVAL-1",
        project_id="rover_v2",
        description="3.3V output >= 2A",
        constraints=[c1, c2],
    )

    # 2. Candidate A: PASS (3.3V, 3A)
    knowledge_graph_service.create_entity("ENT-CAND-A", EntityType.COMPONENT, "TPS62130", "rover_v2")
    knowledge_graph_service.add_specification("S1", "ENT-CAND-A", "output_voltage", "3.3 V", "dsA.pdf", 1)
    knowledge_graph_service.add_specification("S2", "ENT-CAND-A", "output_current", "3 A", "dsA.pdf", 1)

    # 3. Candidate B: FAIL (5.0V, 3A)
    knowledge_graph_service.create_entity("ENT-CAND-B", EntityType.COMPONENT, "LM2596-5", "rover_v2")
    knowledge_graph_service.add_specification("S3", "ENT-CAND-B", "output_voltage", "5.0 V", "dsB.pdf", 1)
    knowledge_graph_service.add_specification("S4", "ENT-CAND-B", "output_current", "3 A", "dsB.pdf", 1)

    # 4. Candidate C: UNKNOWN (3.3V, missing current)
    knowledge_graph_service.create_entity("ENT-CAND-C", EntityType.COMPONENT, "UnknownReg", "rover_v2")
    knowledge_graph_service.add_specification("S5", "ENT-CAND-C", "output_voltage", "3.3 V", "dsC.pdf", 1)


def test_candidate_pass_fail_unknown():
    # Candidate A -> PASS
    val_a = validation_service.validate_candidate("REQ-EVAL-1", "ENT-CAND-A")
    assert val_a.overall_status == ValidationStatus.PASS

    # Candidate B -> FAIL
    val_b = validation_service.validate_candidate("REQ-EVAL-1", "ENT-CAND-B")
    assert val_b.overall_status == ValidationStatus.FAIL

    # Candidate C -> UNKNOWN
    val_c = validation_service.validate_candidate("REQ-EVAL-1", "ENT-CAND-C")
    assert val_c.overall_status == ValidationStatus.UNKNOWN
