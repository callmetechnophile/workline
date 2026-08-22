/**
 * Cache serializer supporting schema versioning and safe deserialization.
 */

import { CacheEntry } from "./metadata";
import { CacheSerializationError } from "./errors";

export const CURRENT_SCHEMA_VERSION = "1.0.0";

export class CacheSerializer {
  public static serialize<T>(entry: CacheEntry<T>): string {
    try {
      return JSON.stringify(entry);
    } catch (err: any) {
      throw new CacheSerializationError(`Failed to serialize cache entry: ${err.message}`);
    }
  }

  public static deserialize<T>(payload: string): CacheEntry<T> | null {
    try {
      const parsed = JSON.parse(payload) as CacheEntry<T>;
      if (!parsed.metadata || !parsed.metadata.cacheKey || parsed.data === undefined) {
        return null;
      }
      return parsed;
    } catch (err: any) {
      return null; // Gracefully discard corrupted entries
    }
  }

  public static validateSchemaVersion(metadata: { schemaVersion: string }): boolean {
    return metadata.schemaVersion === CURRENT_SCHEMA_VERSION;
  }
}
