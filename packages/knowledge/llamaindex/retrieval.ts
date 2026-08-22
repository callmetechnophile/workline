/**
 * Cached retrieval pipeline with SurrealDB authoritative validation.
 */

import { knowledgeCache } from "../cache/cache";
import { CacheKeyGenerator } from "../cache/keys";
import { CacheObjectType } from "../cache/metadata";

export interface RetrievedCandidate {
  id: string;
  type: "DECISION" | "REQUIREMENT" | "FINDING" | "DOCUMENT";
  title: string;
  content: string;
  score: number;
  status?: string; // e.g. APPROVED, SUPERSEDED, REJECTED
}

export class CachedRetrievalPipeline {
  public async retrieve(
    projectId: string,
    query: string,
    indexVersion: number = 1,
    authoritativeStatusMap?: Map<string, string>
  ): Promise<RetrievedCandidate[]> {
    const configHash = "top_k_5_hybrid";
    const cacheKey = CacheKeyGenerator.generateRetrievalKey(projectId, query, configHash, indexVersion);

    // 1. Cache lookup
    const cached = await knowledgeCache.get<RetrievedCandidate[]>(cacheKey, CacheObjectType.RETRIEVAL);
    let candidates: RetrievedCandidate[];

    if (cached) {
      candidates = cached;
    } else {
      // 2. Simulated Qdrant / Hybrid retrieval
      candidates = [
        {
          id: "DEC-101",
          type: "DECISION",
          title: "Select Buck Regulator LM2596",
          content: "Selected for 3A high efficiency power step-down conversion.",
          score: 0.94,
          status: "APPROVED",
        },
        {
          id: "DEC-102",
          type: "DECISION",
          title: "Select LDO TPS7A4700",
          content: "Selected for ultra-low noise RF and sensor rails.",
          score: 0.88,
          status: "SUPERSEDED",
        },
      ];

      // Cache candidate set
      await knowledgeCache.set(cacheKey, candidates, CacheObjectType.RETRIEVAL, {
        projectId,
        ttl: 3600,
      });
    }

    // 3. SurrealDB Authoritative Validation Filter
    // Never present superseded or rejected decisions as current
    if (authoritativeStatusMap) {
      candidates = candidates.map((cand) => {
        const liveStatus = authoritativeStatusMap.get(cand.id);
        if (liveStatus) {
          return { ...cand, status: liveStatus };
        }
        return cand;
      });
    }

    return candidates.filter((c) => c.status !== "SUPERSEDED" && c.status !== "REJECTED");
  }
}
