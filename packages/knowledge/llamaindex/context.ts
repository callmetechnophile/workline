/**
 * Cached agent context builder.
 */

import { knowledgeCache } from "../cache/cache";
import { CacheKeyGenerator } from "../cache/keys";
import { CacheObjectType } from "../cache/metadata";
import { RetrievedCandidate } from "./retrieval";

export class CachedContextBuilder {
  public async buildContext(
    projectId: string,
    query: string,
    knowledgeVersion: number,
    candidates: RetrievedCandidate[]
  ): Promise<string> {
    const cacheKey = CacheKeyGenerator.generateContextKey(projectId, query, knowledgeVersion);

    // 1. Cache lookup
    const cached = await knowledgeCache.get<string>(cacheKey, CacheObjectType.CONTEXT);
    if (cached) {
      return cached;
    }

    // 2. Build context string
    const lines = [
      `=== ENGINEERING CONTEXT FOR PROJECT '${projectId}' (Knowledge v${knowledgeVersion}) ===`,
      `Query: "${query}"`,
      "",
    ];

    for (const c of candidates) {
      lines.push(`[${c.type}] ${c.id}: ${c.title} (Status: ${c.status || 'CURRENT'})`);
      lines.push(c.content);
      lines.push("");
    }

    const context = lines.join("\n");

    // 3. Cache context
    await knowledgeCache.set(cacheKey, context, CacheObjectType.CONTEXT, {
      projectId,
      ttl: 300,
    });

    return context;
  }
}
