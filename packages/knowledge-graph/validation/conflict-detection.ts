/**
 * Specification conflict detector.
 */

import { Specification, SpecificationConflict } from "../entities/entity-schema";

export class ConflictDetector {
  public static detectConflicts(specs: Specification[]): SpecificationConflict[] {
    const conflicts: SpecificationConflict[] = [];
    const grouped = new Map<string, Specification[]>();

    for (const s of specs) {
      const key = `${s.entityId}:${s.property.toLowerCase()}`;
      if (!grouped.has(key)) {
        grouped.set(key, []);
      }
      grouped.get(key)!.push(s);
    }

    for (const [key, group] of grouped.entries()) {
      if (group.length > 1) {
        for (let i = 0; i < group.length; i++) {
          for (let j = i + 1; j < group.length; j++) {
            const specA = group[i];
            const specB = group[j];

            // Compare normalized values
            if (Math.abs(specA.normalizedValue - specB.normalizedValue) > 1e-6) {
              conflicts.push({
                conflictId: `CONF-${specA.entityId}-${Date.now()}-${i}-${j}`,
                entityId: specA.entityId,
                property: specA.property,
                valueA: specA.value,
                sourceA: `${specA.sourceDocument} (P.${specA.page})`,
                valueB: specB.value,
                sourceB: `${specB.sourceDocument} (P.${specB.page})`,
                status: "OPEN",
                createdAt: Date.now(),
              });
            }
          }
        }
      }
    }

    return conflicts;
  }
}
