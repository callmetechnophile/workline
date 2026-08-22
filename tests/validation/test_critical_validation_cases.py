"""Critical acceptance tests for Phase 10F engineering validation."""

import pytest
from backend.workline.knowledge.graph.models import EntityType
from backend.workline.knowledge.graph.service import knowledge_graph_service
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service


def test_critical_four_candidate_scenario():
    # Requirement: 5V input, 3.3V output, >= 2A output current
    c_vin = EngineeringConstraint(
        constraint_id="c_vin",
        property="input_voltage",
        operator=ConstraintOperator.LTE,
        required_value="5V",
        required_unit="V",
        normalized_value=5.0,
    )
    c_vout = EngineeringConstraint(
        constraint_id="c_vout",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
    )
    c_iout = EngineeringConstraint(
        constraint_id="c_iout",
        property="output_current",
        operator=ConstraintOperator.GTE,
        required_value="2A",
        required_unit="A",
        normalized_value=2.0,
    )

    validation_service.create_requirement(
        requirement_id="REQ-CRITICAL-1",
        project_id="rover_v2",
        description="3.3V regulator capable of at least 2A from a 5V source",
        constraints=[c_vin, c_vout, c_iout],
    )

    # Candidate A: Input=5V, Output=3.3V, Current=3A -> PASS
    knowledge_graph_service.create_entity("ENT-TPS62130-A", EntityType.COMPONENT, "TPS62130", "rover_v2")
    knowledge_graph_service.add_specification("S_A1", "ENT-TPS62130-A", "input_voltage", "5.0 V", "dsA.pdf", 1)
    knowledge_graph_service.add_specification("S_A2", "ENT-TPS62130-A", "output_voltage", "3.3 V", "dsA.pdf", 1)
    knowledge_graph_service.add_specification("S_A3", "ENT-TPS62130-A", "output_current", "3 A", "dsA.pdf", 1)

    val_a = validation_service.validate_candidate("REQ-CRITICAL-1", "ENT-TPS62130-A")
    assert val_a.overall_status == ValidationStatus.PASS

    # Candidate B: Input=5V, Output=5V, Current=3A -> FAIL
    knowledge_graph_service.create_entity("ENT-LM2596-B", EntityType.COMPONENT, "LM2596-5", "rover_v2")
    knowledge_graph_service.add_specification("S_B1", "ENT-LM2596-B", "input_voltage", "5.0 V", "dsB.pdf", 1)
    knowledge_graph_service.add_specification("S_B2", "ENT-LM2596-B", "output_voltage", "5.0 V", "dsB.pdf", 1)
    knowledge_graph_service.add_specification("S_B3", "ENT-LM2596-B", "output_current", "3 A", "dsB.pdf", 1)

    val_b = validation_service.validate_candidate("REQ-CRITICAL-1", "ENT-LM2596-B")
    assert val_b.overall_status == ValidationStatus.FAIL

    # Candidate C: Input=5V, Output=3.3V, Current=UNKNOWN -> UNKNOWN
    knowledge_graph_service.create_entity("ENT-REG-C", EntityType.COMPONENT, "UnknownReg", "rover_v2")
    knowledge_graph_service.add_specification("S_C1", "ENT-REG-C", "input_voltage", "5.0 V", "dsC.pdf", 1)
    knowledge_graph_service.add_specification("S_C2", "ENT-REG-C", "output_voltage", "3.3 V", "dsC.pdf", 1)

    val_c = validation_service.validate_candidate("REQ-CRITICAL-1", "ENT-REG-C")
    assert val_c.overall_status == ValidationStatus.UNKNOWN

    # Candidate D: Input=5V, Output=3.3V, Conflicting Current (3A vs 1A) -> CONFLICT
    knowledge_graph_service.create_entity("ENT-REG-D", EntityType.COMPONENT, "ConflictedReg", "rover_v2")
    knowledge_graph_service.add_specification("S_D1", "ENT-REG-D", "input_voltage", "5.0 V", "dsD1.pdf", 1)
    knowledge_graph_service.add_specification("S_D2", "ENT-REG-D", "output_voltage", "3.3 V", "dsD1.pdf", 1)
    knowledge_graph_service.add_specification("S_D3a", "ENT-REG-D", "output_current", "3 A", "dsD1.pdf", 1)
    knowledge_graph_service.add_specification("S_D3b", "ENT-REG-D", "output_current", "1 A", "dsD2.pdf", 2)

    val_d = validation_service.validate_candidate("REQ-CRITICAL-1", "ENT-REG-D")
    assert val_d.overall_status == ValidationStatus.CONFLICT
