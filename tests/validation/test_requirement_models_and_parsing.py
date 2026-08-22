"""Tests for Requirement schemas and Ambiguity detection."""

from backend.workline.validation.ambiguity import AmbiguityDetector
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
)


def test_requirement_model_creation():
    c1 = EngineeringConstraint(
        constraint_id="C1",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
        dimension="VOLTAGE",
    )
    c2 = EngineeringConstraint(
        constraint_id="C2",
        property="output_current",
        operator=ConstraintOperator.GTE,
        required_value="2A",
        required_unit="A",
        normalized_value=2.0,
        dimension="CURRENT",
    )

    req = EngineeringRequirement(
        requirement_id="REQ-TEST-1",
        project_id="rover_v2",
        category=RequirementCategory.POWER,
        description="Need a 3.3V regulator from 5V input capable of at least 2A.",
        constraints=[c1, c2],
    )

    assert req.requirement_id == "REQ-TEST-1"
    assert len(req.constraints) == 2
    assert req.constraints[0].normalized_value == 3.3


def test_ambiguity_detection():
    amb_1 = AmbiguityDetector.checkAmbiguity("Need a low power buck regulator.")
    assert amb_1["isAmbiguous"] is True
    assert "low power" in amb_1["detectedTerms"]

    amb_2 = AmbiguityDetector.checkAmbiguity("Output voltage = 3.3V, output current >= 2A.")
    assert amb_2["isAmbiguous"] is False
