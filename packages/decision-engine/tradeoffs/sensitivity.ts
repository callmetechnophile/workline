/**
 * Weight Sensitivity and Stability Analysis Engine.
 */

import { DecisionCandidate, DecisionCriterion } from "../criteria/criterion-types";
import { DeterministicScorer } from "../evaluation/score";

export type DecisionStability = "ROBUST" | "MODERATELY_STABLE" | "SENSITIVE" | "UNSTABLE";

export interface SensitivityAnalysisResult {
  criterionId: string;
  originalWeight: number;
  testedWeight: number;
  originalWinner: string;
  newWinner: string;
  isRankingChanged: boolean;
}

export class SensitivityAnalyzer {
  public static analyze(
    candidates: DecisionCandidate[],
    criteria: DecisionCriterion[],
    rawMatrix: Record<string, Record<string, number>>
  ): { stability: DecisionStability; analyses: SensitivityAnalysisResult[] } {
    if (candidates.length < 2) {
      return { stability: "ROBUST", analyses: [] };
    }

    // Determine base winner
    const baseScores = candidates.map((c) => ({
      name: c.name,
      score: DeterministicScorer.calculateCandidateScore(c, criteria, rawMatrix[c.candidateId] || {}).totalScore,
    }));
    baseScores.sort((a, b) => b.score - a.score);
    const baseWinner = baseScores[0].name;

    const analyses: SensitivityAnalysisResult[] = [];
    let rankChanges = 0;

    for (const crit of criteria) {
      // Perturb weight by +50% and -50%
      for (const factor of [0.5, 1.5]) {
        const perturbed = criteria.map((c) =>
          c.criterionId === crit.criterionId ? { ...c, weight: c.weight * factor } : c
        );

        const perturbedScores = candidates.map((c) => ({
          name: c.name,
          score: DeterministicScorer.calculateCandidateScore(c, perturbed, rawMatrix[c.candidateId] || {}).totalScore,
        }));
        perturbedScores.sort((a, b) => b.score - a.score);
        const newWinner = perturbedScores[0].name;

        if (newWinner !== baseWinner) {
          rankChanges++;
          analyses.push({
            criterionId: crit.criterionId,
            originalWeight: crit.weight,
            testedWeight: Number((crit.weight * factor).toFixed(2)),
            originalWinner: baseWinner,
            newWinner,
            isRankingChanged: true,
          });
        }
      }
    }

    let stability: DecisionStability = "ROBUST";
    if (rankChanges > 2) {
      stability = "UNSTABLE";
    } else if (rankChanges > 0) {
      stability = "SENSITIVE";
    }

    return { stability, analyses };
  }
}
