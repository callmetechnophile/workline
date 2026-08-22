/**
 * Prioritized Entity Resolution Engine.
 */

import { CanonicalEntity, EntityMention } from "./entity-schema";
import { EntityStatus, EntityType } from "./entity-types";

export interface ResolutionMatch {
  status: "RESOLVED" | "ALIAS_VARIANT" | "UNRESOLVED";
  canonicalEntityId?: string;
  matchedEntity?: CanonicalEntity;
  confidence: number;
  strategy: string;
  reason: string;
}

export class EntityResolver {
  public static resolveMention(
    mention: EntityMention,
    existingEntities: CanonicalEntity[],
    manufacturerContext?: string
  ): ResolutionMatch {
    const mentionText = mention.originalText.trim().toUpperCase();
    const normText = mention.normalizedText.trim().toUpperCase();

    // 1. Exact Canonical Name Match
    for (const ent of existingEntities) {
      if (ent.canonicalName.toUpperCase() === mentionText) {
        return {
          status: "RESOLVED",
          canonicalEntityId: ent.entityId,
          matchedEntity: ent,
          confidence: 1.0,
          strategy: "EXACT_CANONICAL_MATCH",
          reason: `Exact match with canonical entity '${ent.canonicalName}'`,
        };
      }
    }

    // 2. Manufacturer + Part Number Match
    if (manufacturerContext) {
      const mfrUpper = manufacturerContext.trim().toUpperCase();
      for (const ent of existingEntities) {
        if (
          ent.manufacturer?.toUpperCase() === mfrUpper &&
          (ent.basePartNumber?.toUpperCase() === mentionText || ent.canonicalName.toUpperCase() === mentionText)
        ) {
          return {
            status: "RESOLVED",
            canonicalEntityId: ent.entityId,
            matchedEntity: ent,
            confidence: 0.98,
            strategy: "MANUFACTURER_PART_MATCH",
            reason: `Matched with manufacturer '${ent.manufacturer}' and part number '${mentionText}'`,
          };
        }
      }
    }

    // 3. Known Aliases Match
    for (const ent of existingEntities) {
      if (ent.aliases.some((a) => a.toUpperCase() === mentionText || a.toUpperCase() === normText)) {
        return {
          status: "RESOLVED",
          canonicalEntityId: ent.entityId,
          matchedEntity: ent,
          confidence: 0.95,
          strategy: "ALIAS_MATCH",
          reason: `Matched known alias for entity '${ent.canonicalName}'`,
        };
      }
    }

    // 4. Base Part Number & Package Variant Check (e.g. TPS62130 vs TPS62130RGTR)
    for (const ent of existingEntities) {
      const canonUpper = ent.canonicalName.toUpperCase();
      if (mentionText.startsWith(canonUpper) || canonUpper.startsWith(mentionText)) {
        return {
          status: "ALIAS_VARIANT",
          canonicalEntityId: ent.entityId,
          matchedEntity: ent,
          confidence: 0.85,
          strategy: "PART_NUMBER_VARIANT",
          reason: `Packaging or order code variant of base part '${ent.canonicalName}'`,
        };
      }
    }

    // 5. Unresolved (Preserve ambiguity, do not blindly merge)
    return {
      status: "UNRESOLVED",
      confidence: 0.2,
      strategy: "UNRESOLVED",
      reason: `No high-confidence match found for '${mention.originalText}'. Retaining as unresolved mention.`,
    };
  }
}
