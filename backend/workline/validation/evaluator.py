"""Deterministic numerical constraint evaluator."""

from typing import NamedTuple, Optional
from backend.workline.validation.models import (
    ConstraintOperator,
    EngineeringConstraint,
    ValidationStatus,
)
from backend.workline.validation.units import UnitValidator


class EvaluationOutcome(NamedTuple):
    status: ValidationStatus
    reason: str


class DeterministicConstraintEvaluator:
    """Evaluates constraints deterministically with unit and tolerance safety."""

    @classmethod
    def evaluate(
        cls,
        constraint: EngineeringConstraint,
        actual_val: float,
        actual_unit: Optional[str] = None,
    ) -> EvaluationOutcome:
        normalized_actual = actual_val

        # Check unit compatibility and convert if necessary
        if constraint.required_unit and actual_unit and constraint.required_unit != actual_unit:
            success, conv_val, err = UnitValidator.convert(actual_val, actual_unit, constraint.required_unit)
            if not success:
                return EvaluationOutcome(
                    status=ValidationStatus.FAIL,
                    reason=err or "Incompatible unit conversion",
                )
            normalized_actual = conv_val

        required = constraint.normalized_value
        op = constraint.operator

        # Calculate bounds if tolerance is given
        lower_bound = required
        upper_bound = required

        if constraint.tolerance:
            tol_type = constraint.tolerance.get("type", "RELATIVE")
            tol_val = float(constraint.tolerance.get("value", 0.0))
            if tol_type == "RELATIVE":
                delta = abs(required * tol_val)
                lower_bound = required - delta
                upper_bound = required + delta
            else:
                lower_bound = required - tol_val
                upper_bound = required + tol_val

        if op == ConstraintOperator.EQ:
            pass_check = lower_bound - 1e-4 <= normalized_actual <= upper_bound + 1e-4
            return EvaluationOutcome(
                status=ValidationStatus.PASS if pass_check else ValidationStatus.FAIL,
                reason=f"{normalized_actual} matches {required}" if pass_check else f"{normalized_actual} != {required}",
            )

        elif op == ConstraintOperator.GTE:
            pass_check = normalized_actual >= lower_bound - 1e-5
            return EvaluationOutcome(
                status=ValidationStatus.PASS if pass_check else ValidationStatus.FAIL,
                reason=f"{normalized_actual} >= {required}" if pass_check else f"{normalized_actual} < {required}",
            )

        elif op == ConstraintOperator.GT:
            pass_check = normalized_actual > lower_bound + 1e-5
            return EvaluationOutcome(
                status=ValidationStatus.PASS if pass_check else ValidationStatus.FAIL,
                reason=f"{normalized_actual} > {required}" if pass_check else f"{normalized_actual} <= {required}",
            )

        elif op == ConstraintOperator.LTE:
            pass_check = normalized_actual <= upper_bound + 1e-5
            return EvaluationOutcome(
                status=ValidationStatus.PASS if pass_check else ValidationStatus.FAIL,
                reason=f"{normalized_actual} <= {required}" if pass_check else f"{normalized_actual} > {required}",
            )

        elif op == ConstraintOperator.LT:
            pass_check = normalized_actual < upper_bound - 1e-5
            return EvaluationOutcome(
                status=ValidationStatus.PASS if pass_check else ValidationStatus.FAIL,
                reason=f"{normalized_actual} < {required}" if pass_check else f"{normalized_actual} >= {required}",
            )

        return EvaluationOutcome(
            status=ValidationStatus.UNKNOWN,
            reason=f"Operator '{op}' not supported for numeric evaluation",
        )
