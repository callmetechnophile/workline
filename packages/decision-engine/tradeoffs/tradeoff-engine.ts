/**
 * Pairwise and multi-candidate trade-off analysis engine.
 */

import { DecisionCandidate, DecisionCriterion } from "../criteria/criterion-types";

export interface PairwiseTradeoff {
  candidateA: string;
  candidateB: string;
  criterion: string;
  advantageCandidate: string;
  disadvantageCandidate: string;
  scoreDelta: number;
}

export class TradeoffEngine {
  public static comparePairwise(
    candidateA: DecisionCandidate,
    candidateB: DecisionCandidate,
    criteria: DecisionCriterion[]
  ): PairwiseTradeoff[] {
    const tradeoffs: PairwiseTradeoff[] = [];

    for (const c of criteria) {
      const scoreA = candidateA.criterionScores[c.criterionId] ?? 0.0;
      const scoreB = candidateB.criterionScores[c.criterionId] ?? 0.0;
      const diff = scoreA - scoreB;

      if (Math.abs(diff) > 0.05) {
        tradeoffs.push({
          candidateA: candidateA.name,
          candidateB: candidateB.name,
          criterion: c.name,
          advantageCandidate: diff > 0 ? candidateA.name : candidateB.name,
          disadvantageCandidate: diff > 0 ? candidateB.name : candidateA.name,
          scoreDelta: Number(Math.abs(diff).toFixed(3)),
        });
      }
    }

    return tradeoffs;
  }
}
