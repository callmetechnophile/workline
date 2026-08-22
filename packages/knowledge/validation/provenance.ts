/**
 * Provenance tracking and source verification.
 */

import { CacheEntry } from "../cache/metadata";

export class ProvenanceValidator {
  public static verifyProvenance(entry: CacheEntry): boolean {
    return !!(entry.metadata.projectId && entry.metadata.createdAt > 0);
  }
}
