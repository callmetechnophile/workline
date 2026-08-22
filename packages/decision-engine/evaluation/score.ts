/**
 * Deterministic multi-criteria scoring and normalization engine.
 */

import { CriterionDirection, DecisionCandidate, DecisionCriterion } from "../criteria/criterion-types";

export type UncertaintyPolicy = "STRICT" | "CONSERVATIVE" | "NEUTRAL";

export class DeterministicScorer {
  public static calculateCandidateScore(
    candidate: DecisionCandidate,
    criteria: DecisionCriterion[],
    rawValues: Record<string, number | undefined>,
    policy: UncertaintyPolicy = "CONSERVATIVE"
  ): { totalScore: number; criterionScores: Record<string, number> } {
    let totalScore = 0.0;
    let totalWeight = 0.0;
    const criterionScores: Record<string, number> = {};

    for (const crit of criteria) {
      const val = rawValues[crit.criterionId];
      let score = 0.0;

      if (val === undefined) {
        if (policy === "STRICT") {
          score = 0.0;
        } else if (policy === "CONSERVATIVE") {
          score = 0.2; // Penalize missing data
        } else {
          continue; // NEUTRAL: exclude from total weight
        }
      } else {
        if (crit.direction === CriterionDirection.MAXIMIZE) {
          score = Math.min(Math.max(val, 0.0), 1.0);
        } else if (crit.direction === CriterionDirection.MINIMIZE) {
          score = Math.max(0.0, 1.0 - Math.min(val, 1.0));
        } else if (crit.direction === CriterionDirection.TARGET && crit.targetValue !== undefined) {
          const diff = Math.abs(val - crit.targetValue);
          score = Math.max(0.0, 1.0 - diff / (crit.targetValue || 1.0));
        } else {
          score = Math.min(Math.max(val, 0.0), 1.0);
        }
      }

      criterionScores[crit.criterionId] = score;
      totalScore += score * crit.weight;
      totalWeight += crit.weight;
    }

    const normalizedTotal = totalWeight > 0 ? totalScore / totalWeight : 0.0;
    return {
      totalScore: Number(normalizedTotal.toFixed(4)),
      criterionScores,
    };
  }
}
