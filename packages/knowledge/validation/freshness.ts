/**
 * Cache Freshness and Invalidation validator.
 */

import { CacheEntry } from "../cache/metadata";

export class FreshnessValidator {
  public static isFresh(entry: CacheEntry, currentSourceHash?: string): boolean {
    // 1. Check TTL expiry
    if (entry.metadata.expiresAt > 0 && Date.now() > entry.metadata.expiresAt) {
      return false;
    }

    // 2. Check source content hash if provided
    if (currentSourceHash && entry.metadata.sourceHash) {
      if (entry.metadata.sourceHash !== currentSourceHash) {
        return false;
      }
    }

    return true;
  }
}
