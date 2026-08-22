"""Tests for numerical dimension mismatch rejection and project isolation."""

import pytest
from backend.workline.validation.evaluator import DeterministicConstraintEvaluator
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.service import validation_service


def test_incompatible_dimension_rejection():
    # Attempting to compare 3.3V requirement against a 3.3A actual value
    c_volt = EngineeringConstraint(
        constraint_id="c_v",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
        dimension="VOLTAGE",
    )

    outcome = DeterministicConstraintEvaluator.evaluate(c_volt, 3.3, "A")
    assert outcome.status == ValidationStatus.FAIL
    assert "Incompatible dimensions" in outcome.reason


def test_project_isolation_in_requirements():
    validation_service.create_requirement(
        requirement_id="REQ-PROJ-A",
        project_id="rover_v2",
        description="Requirement for rover_v2",
    )
    validation_service.create_requirement(
        requirement_id="REQ-PROJ-B",
        project_id="drone_v1",
        description="Requirement for drone_v1",
    )

    rover_reqs = validation_service.list_requirements(project_id="rover_v2")
    assert any(r.requirement_id == "REQ-PROJ-A" for r in rover_reqs)
    assert not any(r.requirement_id == "REQ-PROJ-B" for r in rover_reqs)
