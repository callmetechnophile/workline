/**
 * Decision lifecycle, human approval, and supersession manager.
 */

import { DecisionStatus, DecisionType, EngineeringDecision } from "../criteria/criterion-types";

export class DecisionLifecycleManager {
  public static approveDecision(
    decision: EngineeringDecision,
    approvedBy: string,
    role: string = "ENGINEER"
  ): EngineeringDecision {
    return {
      ...decision,
      status: DecisionStatus.APPROVED,
      approvedBy: `${approvedBy} (${role})`,
      approvedAt: Date.now(),
      updatedAt: Date.now(),
    };
  }

  public static rejectDecision(
    decision: EngineeringDecision,
    rejectedBy: string,
    reason: string
  ): EngineeringDecision {
    return {
      ...decision,
      status: DecisionStatus.REJECTED,
      rationale: `Rejected by ${rejectedBy}: ${reason}`,
      updatedAt: Date.now(),
    };
  }

  public static supersedeDecision(
    oldDecision: EngineeringDecision,
    newDecisionId: string
  ): EngineeringDecision {
    return {
      ...oldDecision,
      status: DecisionStatus.SUPERSEDED,
      supersededBy: newDecisionId,
      updatedAt: Date.now(),
    };
  }
}
