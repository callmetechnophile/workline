/**
 * Project and Team boundary scope validation.
 */

import { CacheEntry } from "../cache/metadata";
import { CacheIsolationError } from "../cache/errors";

export class ProjectScopeValidator {
  public static validateScope(
    entry: CacheEntry,
    requestProjectId: string,
    requestTeamId?: string
  ): void {
    if (entry.metadata.projectId !== requestProjectId) {
      throw new CacheIsolationError(
        `Cross-project cache access prohibited (Entry: ${entry.metadata.projectId}, Request: ${requestProjectId})`
      );
    }

    if (requestTeamId && entry.metadata.teamId && entry.metadata.teamId !== requestTeamId) {
      throw new CacheIsolationError(
        `Cross-team cache access prohibited (Entry: ${entry.metadata.teamId}, Request: ${requestTeamId})`
      );
    }
  }
}
