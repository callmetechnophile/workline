/**
 * Validation result models and candidate evaluator.
 */

import { EngineeringConstraint, EngineeringRequirement, ValidationStatus } from "../requirements/requirement-schema";
import { ConstraintEvaluator } from "../constraints/comparison";

export interface ConstraintResult {
  constraintId: string;
  property: string;
  requiredValue: string;
  actualValue: string;
  operator: string;
  status: ValidationStatus;
  unit?: string;
  sourceDocument?: string;
  page?: number;
  reason: string;
}

export interface ValidationResult {
  validationId: string;
  candidateId: string;
  requirementId: string;
  overallStatus: ValidationStatus;
  constraintResults: ConstraintResult[];
  conflicts: string[];
  warnings: string[];
  ruleVersion: string;
  knowledgeVersion: string;
  createdAt: number;
}

export class CandidateEvaluator {
  public static evaluateCandidate(
    candidateId: string,
    requirement: EngineeringRequirement,
    specs: Record<string, { value: number; unit?: string; raw: string; doc?: string; page?: number; isConflict?: boolean }>,
    ruleVersion: string = "v1"
  ): ValidationResult {
    const results: ConstraintResult[] = [];
    const conflicts: string[] = [];
    const warnings: string[] = [];
    let hasFail = false;
    let hasUnknown = false;
    let hasConflict = false;

    for (const c of requirement.constraints) {
      const spec = specs[c.property.toLowerCase()] || specs[c.property];

      if (!spec) {
        results.push({
          constraintId: c.constraintId,
          property: c.property,
          requiredValue: `${c.operator} ${c.requiredValue}`,
          actualValue: "UNKNOWN",
          operator: c.operator,
          status: ValidationStatus.UNKNOWN,
          reason: `No specification found for property '${c.property}' in candidate documentation`,
        });
        hasUnknown = true;
        continue;
      }

      if (spec.isConflict) {
        results.push({
          constraintId: c.constraintId,
          property: c.property,
          requiredValue: `${c.operator} ${c.requiredValue}`,
          actualValue: spec.raw,
          operator: c.operator,
          status: ValidationStatus.CONFLICT,
          sourceDocument: spec.doc,
          page: spec.page,
          reason: `Contradictory specifications detected across documents for '${c.property}'`,
        });
        conflicts.push(`Conflict in ${c.property}: ${spec.raw}`);
        hasConflict = true;
        continue;
      }

      const outcome = ConstraintEvaluator.evaluate(c, spec.value, spec.unit);
      results.push({
        constraintId: c.constraintId,
        property: c.property,
        requiredValue: `${c.operator} ${c.requiredValue}`,
        actualValue: spec.raw,
        operator: c.operator,
        status: outcome.status,
        unit: spec.unit,
        sourceDocument: spec.doc,
        page: spec.page,
        reason: outcome.reason,
      });

      if (outcome.status === ValidationStatus.FAIL) hasFail = true;
      if (outcome.status === ValidationStatus.UNKNOWN) hasUnknown = true;
    }

    let overall: ValidationStatus = ValidationStatus.PASS;
    if (hasFail) {
      overall = ValidationStatus.FAIL;
    } else if (hasConflict) {
      overall = ValidationStatus.CONFLICT;
    } else if (hasUnknown) {
      overall = ValidationStatus.UNKNOWN;
    }

    return {
      validationId: `VAL-${candidateId}-${requirement.requirementId}-${Date.now()}`,
      candidateId,
      requirementId: requirement.requirementId,
      overallStatus: overall,
      constraintResults: results,
      conflicts,
      warnings,
      ruleVersion,
      knowledgeVersion: "1.0.0",
      createdAt: Date.now(),
    };
  }
}
