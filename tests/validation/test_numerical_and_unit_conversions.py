"""Tests for deterministic unit conversion, dimensional safety, and tolerance bounds."""

import pytest
from backend.workline.validation.evaluator import DeterministicConstraintEvaluator
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.units import UnitValidator


def test_unit_validator_conversions():
    # Voltage (mV to V)
    succ, val, err = UnitValidator.convert(3300.0, "mV", "V")
    assert succ is True and abs(val - 3.3) < 1e-5

    # Current (mA to A)
    succ, val, err = UnitValidator.convert(500.0, "mA", "A")
    assert succ is True and abs(val - 0.5) < 1e-5

    # Frequency (MHz to Hz)
    succ, val, err = UnitValidator.convert(16.0, "MHz", "Hz")
    assert succ is True and abs(val - 16000000.0) < 1e-5

    # Incompatible dimensions (Voltage vs Current)
    succ, val, err = UnitValidator.convert(3.3, "V", "A")
    assert succ is False
    assert "Incompatible dimensions" in err


def test_numerical_comparisons_and_tolerances():
    # 1. GTE comparison
    c_gte = EngineeringConstraint(
        constraint_id="c1",
        property="output_current",
        operator=ConstraintOperator.GTE,
        required_value="2A",
        required_unit="A",
        normalized_value=2.0,
    )
    res_pass = DeterministicConstraintEvaluator.evaluate(c_gte, 3.0, "A")
    assert res_pass.status == ValidationStatus.PASS

    res_fail = DeterministicConstraintEvaluator.evaluate(c_gte, 1.5, "A")
    assert res_fail.status == ValidationStatus.FAIL

    # 2. Relative Tolerance (3.3V +- 5%) -> [3.135, 3.465]
    c_tol = EngineeringConstraint(
        constraint_id="c2",
        property="output_voltage",
        operator=ConstraintOperator.EQ,
        required_value="3.3V",
        required_unit="V",
        normalized_value=3.3,
        tolerance={"type": "RELATIVE", "value": 0.05},
    )
    assert DeterministicConstraintEvaluator.evaluate(c_tol, 3.4, "V").status == ValidationStatus.PASS
    assert DeterministicConstraintEvaluator.evaluate(c_tol, 3.6, "V").status == ValidationStatus.FAIL
