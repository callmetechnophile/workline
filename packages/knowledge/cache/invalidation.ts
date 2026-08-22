/**
 * Invalidation engine tracking dependencies and project invalidation rules.
 */

import { CacheEntry, CacheObjectType } from "./metadata";

export class InvalidationEngine {
  private sourceToKeys: Map<string, Set<string>> = new Map();
  private projectToKeys: Map<string, Set<string>> = new Map();

  public track(entry: CacheEntry): void {
    const key = entry.metadata.cacheKey;
    const proj = entry.metadata.projectId;
    const src = entry.metadata.sourceId;

    if (proj) {
      if (!this.projectToKeys.has(proj)) {
        this.projectToKeys.set(proj, new Set());
      }
      this.projectToKeys.get(proj)!.add(key);
    }

    if (src) {
      if (!this.sourceToKeys.has(src)) {
        this.sourceToKeys.set(src, new Set());
      }
      this.sourceToKeys.get(src)!.add(key);
    }
  }

  public getKeysBySource(sourceId: string): string[] {
    const set = this.sourceToKeys.get(sourceId);
    return set ? Array.from(set) : [];
  }

  public getKeysByProject(projectId: string): string[] {
    const set = this.projectToKeys.get(projectId);
    return set ? Array.from(set) : [];
  }

  public removeKey(key: string): void {
    for (const set of this.sourceToKeys.values()) {
      set.delete(key);
    }
    for (const set of this.projectToKeys.values()) {
      set.delete(key);
    }
  }

  public clear(): void {
    this.sourceToKeys.clear();
    this.projectToKeys.clear();
  }
}
