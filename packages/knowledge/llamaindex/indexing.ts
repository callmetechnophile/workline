/**
 * Cached indexing manager tracking Qdrant index versions.
 */

import { knowledgeCache } from "../cache/cache";

export class CachedIndexingManager {
  private projectIndexVersions: Map<string, number> = new Map();

  public getIndexVersion(projectId: string): number {
    return this.projectIndexVersions.get(projectId) ?? 1;
  }

  public incrementIndexVersion(projectId: string): number {
    const next = this.getIndexVersion(projectId) + 1;
    this.projectIndexVersions.set(projectId, next);
    // Invalidate project retrieval caches
    knowledgeCache.invalidateByProject(projectId);
    return next;
  }
}
