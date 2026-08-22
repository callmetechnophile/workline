/**
 * Deterministic cache key generator for Knowledge Cache.
 */

import { createHash } from "crypto";
import { CacheObjectType } from "./metadata";

export class CacheKeyGenerator {
  public static hash(input: string): string {
    return createHash("sha256").update(input).digest("hex");
  }

  public static generateKey(
    objectType: CacheObjectType,
    projectId: string,
    identifier: string,
    configHash?: string,
    indexVersion?: number
  ): string {
    const safeIdentifier = identifier.length > 64 ? this.hash(identifier) : identifier.replace(/[^a-zA-Z0-9_-]/g, "_");
    const parts = ["workline", "knowledge", objectType.toLowerCase(), projectId, safeIdentifier];

    if (configHash) {
      parts.push(configHash.slice(0, 16));
    }
    if (indexVersion !== undefined) {
      parts.push(`v${indexVersion}`);
    }

    return parts.join(":");
  }

  public static generateEmbeddingKey(
    contentHash: string,
    model: string,
    version: string = "v1",
    dimension: number = 384
  ): string {
    return `workline:knowledge:embedding:${contentHash.slice(0, 24)}:${model}:${version}:${dimension}`;
  }

  public static generateRetrievalKey(
    projectId: string,
    query: string,
    retrievalConfigHash: string,
    indexVersion: number = 1
  ): string {
    const queryHash = this.hash(query).slice(0, 24);
    return `workline:knowledge:retrieval:${projectId}:${queryHash}:${retrievalConfigHash.slice(0, 12)}:idx${indexVersion}`;
  }

  public static generateContextKey(
    projectId: string,
    query: string,
    knowledgeVersion: number
  ): string {
    const queryHash = this.hash(query).slice(0, 24);
    return `workline:knowledge:context:${projectId}:${queryHash}:kv${knowledgeVersion}`;
  }
}
