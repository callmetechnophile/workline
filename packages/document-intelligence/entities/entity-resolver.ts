/**
 * Resolves and merges engineering entities safely.
 */

import { EngineeringEntity } from "./engineering-entities";

export enum ResolutionStatus {
  MATCHED = "MATCHED",
  ALIAS = "ALIAS",
  UNRESOLVED = "UNRESOLVED",
}

export interface ResolutionResult {
  status: ResolutionStatus;
  canonicalId: string;
  confidence: number;
  reason: string;
}

export class EntityResolver {
  public static resolve(entityA: EngineeringEntity, entityB: EngineeringEntity): ResolutionResult {
    // Exact match
    if (entityA.normalizedValue.toUpperCase() === entityB.normalizedValue.toUpperCase()) {
      return {
        status: ResolutionStatus.MATCHED,
        canonicalId: entityA.entityId,
        confidence: 1.0,
        reason: "Exact case-insensitive match",
      };
    }

    // Part number packaging suffix check (e.g. TPS62130 vs TPS62130RGTR)
    const valA = entityA.normalizedValue.toUpperCase();
    const valB = entityB.normalizedValue.toUpperCase();

    if (valB.startsWith(valA) || valA.startsWith(valB)) {
      return {
        status: ResolutionStatus.ALIAS,
        canonicalId: valA.length <= valB.length ? entityA.entityId : entityB.entityId,
        confidence: 0.85,
        reason: "Base part number match with package suffix",
      };
    }

    // Do not blindly merge different parts
    return {
      status: ResolutionStatus.UNRESOLVED,
      canonicalId: entityA.entityId,
      confidence: 0.2,
      reason: "Distinct part numbers or ambiguous context",
    };
  }
}
