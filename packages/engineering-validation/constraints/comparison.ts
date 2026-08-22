/**
 * Deterministic constraint evaluation and comparison logic.
 */

import { ConstraintOperator, EngineeringConstraint, ValidationStatus } from "../requirements/requirement-schema";
import { UnitConverter } from "../units/unit-converter";

export interface EvaluationOutcome {
  status: ValidationStatus;
  reason: string;
}

export class ConstraintEvaluator {
  public static evaluate(
    constraint: EngineeringConstraint,
    actualValueNum: number,
    actualUnitStr?: string
  ): EvaluationOutcome {
    let normalizedActual = actualValueNum;

    // Unit conversion if units are specified and different
    if (constraint.requiredUnit && actualUnitStr && constraint.requiredUnit !== actualUnitStr) {
      const conv = UnitConverter.convert(actualValueNum, actualUnitStr, constraint.requiredUnit);
      if (!conv.success) {
        return {
          status: ValidationStatus.FAIL,
          reason: conv.error || "Unit conversion failure",
        };
      }
      normalizedActual = conv.convertedValue!;
    }

    const required = constraint.normalizedValue;
    const op = constraint.operator;

    // Calculate tolerance bounds if specified
    let lowerBound = required;
    let upperBound = required;

    if (constraint.tolerance) {
      if (constraint.tolerance.type === "RELATIVE") {
        const delta = Math.abs(required * constraint.tolerance.value);
        lowerBound = required - delta;
        upperBound = required + delta;
      } else {
        lowerBound = required - constraint.tolerance.value;
        upperBound = required + constraint.tolerance.value;
      }
    }

    switch (op) {
      case ConstraintOperator.EQ: {
        const pass = constraint.tolerance
          ? normalizedActual >= lowerBound && normalizedActual <= upperBound
          : Math.abs(normalizedActual - required) < 1e-4;
        return {
          status: pass ? ValidationStatus.PASS : ValidationStatus.FAIL,
          reason: pass
            ? `${normalizedActual} matches required ${required}`
            : `${normalizedActual} does not equal required ${required}`,
        };
      }
      case ConstraintOperator.GTE: {
        const pass = normalizedActual >= lowerBound - 1e-6;
        return {
          status: pass ? ValidationStatus.PASS : ValidationStatus.FAIL,
          reason: pass
            ? `${normalizedActual} >= ${required}`
            : `${normalizedActual} < required ${required}`,
        };
      }
      case ConstraintOperator.GT: {
        const pass = normalizedActual > lowerBound + 1e-6;
        return {
          status: pass ? ValidationStatus.PASS : ValidationStatus.FAIL,
          reason: pass
            ? `${normalizedActual} > ${required}`
            : `${normalizedActual} <= required ${required}`,
        };
      }
      case ConstraintOperator.LTE: {
        const pass = normalizedActual <= upperBound + 1e-6;
        return {
          status: pass ? ValidationStatus.PASS : ValidationStatus.FAIL,
          reason: pass
            ? `${normalizedActual} <= ${required}`
            : `${normalizedActual} > required ${required}`,
        };
      }
      case ConstraintOperator.LT: {
        const pass = normalizedActual < upperBound - 1e-6;
        return {
          status: pass ? ValidationStatus.PASS : ValidationStatus.FAIL,
          reason: pass
            ? `${normalizedActual} < ${required}`
            : `${normalizedActual} >= required ${required}`,
        };
      }
      default:
        return {
          status: ValidationStatus.UNKNOWN,
          reason: `Unsupported operator '${op}' for numeric evaluation`,
        };
    }
  }
}
