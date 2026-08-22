/**
 * Unified KnowledgeCache coordinating L1 memory and L2 persistent storage.
 */

import {
  CacheEntry,
  CacheMetadata,
  CacheObjectType,
  CacheOptions,
  CacheStats,
} from "./metadata";
import { MemoryCache } from "./memory";
import { PersistentCache } from "./persistent";
import { InvalidationEngine } from "./invalidation";
import { CURRENT_SCHEMA_VERSION } from "./serializer";

export class KnowledgeCache {
  private l1: MemoryCache;
  private l2: PersistentCache;
  private invalidation: InvalidationEngine;
  private stats: CacheStats;

  constructor(
    l1MaxEntries: number = 2000,
    l2BaseDir: string = ".workline/cache"
  ) {
    this.l1 = new MemoryCache(l1MaxEntries);
    this.l2 = new PersistentCache(l2BaseDir);
    this.invalidation = new InvalidationEngine();
    this.stats = {
      hits: 0,
      misses: 0,
      evictions: 0,
      expired: 0,
      invalidations: 0,
      l1Entries: 0,
      l2Entries: 0,
      l2SizeBytes: 0,
      hitRate: 0.0,
      missRate: 0.0,
    };
  }

  public async get<T>(key: string, objectType: CacheObjectType = CacheObjectType.RETRIEVAL): Promise<T | null> {
    // 1. Try L1 Memory
    const l1Entry = this.l1.get<T>(key);
    if (l1Entry) {
      this.recordHit();
      return l1Entry.data;
    }

    // 2. Try L2 Persistent
    const l2Entry = this.l2.get<T>(key, objectType);
    if (l2Entry) {
      // Promote to L1
      this.l1.set(l2Entry);
      this.recordHit();
      return l2Entry.data;
    }

    this.recordMiss();
    return null;
  }

  public async set<T>(
    key: string,
    value: T,
    objectType: CacheObjectType,
    options: CacheOptions
  ): Promise<void> {
    const now = Date.now();
    const ttlSeconds = options.ttl ?? this.getDefaultTtl(objectType);
    const expiresAt = ttlSeconds > 0 ? now + ttlSeconds * 1000 : 0;

    const metadata: CacheMetadata = {
      cacheKey: key,
      objectType,
      projectId: options.projectId,
      teamId: options.teamId ?? "default_team",
      sourceId: options.sourceId,
      sourceHash: options.sourceHash,
      schemaVersion: options.schemaVersion ?? CURRENT_SCHEMA_VERSION,
      createdAt: now,
      expiresAt,
      projectVersion: options.projectVersion,
      gitCommit: options.gitCommit,
      provider: options.provider,
      model: options.model,
      embeddingDimension: options.embeddingDimension,
      sizeBytes: JSON.stringify(value).length,
    };

    const entry: CacheEntry<T> = { metadata, data: value };

    // Write to L1 and L2
    this.l1.set(entry);
    this.l2.set(entry);
    this.invalidation.track(entry);
  }

  public async has(key: string, objectType: CacheObjectType = CacheObjectType.RETRIEVAL): Promise<boolean> {
    return (await this.get(key, objectType)) !== null;
  }

  public async delete(key: string, objectType: CacheObjectType = CacheObjectType.RETRIEVAL): Promise<boolean> {
    this.l1.delete(key);
    const deletedL2 = this.l2.delete(key, objectType);
    this.invalidation.removeKey(key);
    return deletedL2;
  }

  public async invalidateBySource(sourceId: string): Promise<number> {
    const keys = this.invalidation.getKeysBySource(sourceId);
    for (const k of keys) {
      this.l1.delete(k);
      for (const t of Object.values(CacheObjectType)) {
        this.l2.delete(k, t as CacheObjectType);
      }
    }
    this.stats.invalidations += keys.length;
    return keys.length;
  }

  public async invalidateByProject(projectId: string): Promise<number> {
    const keys = this.invalidation.getKeysByProject(projectId);
    for (const k of keys) {
      this.l1.delete(k);
      for (const t of Object.values(CacheObjectType)) {
        this.l2.delete(k, t as CacheObjectType);
      }
    }
    this.stats.invalidations += keys.length;
    return keys.length;
  }

  public async clear(): Promise<void> {
    this.l1.clear();
    this.l2.clear();
    this.invalidation.clear();
  }

  public async clearExpired(): Promise<number> {
    const l1Expired = this.l1.clearExpired();
    this.stats.expired += l1Expired;
    return l1Expired;
  }

  public getStats(): CacheStats {
    const l2Stats = this.l2.getStats();
    this.stats.l1Entries = this.l1.size();
    this.stats.l2Entries = l2Stats.totalEntries;
    this.stats.l2SizeBytes = l2Stats.totalSizeBytes;

    const totalReqs = this.stats.hits + this.stats.misses;
    this.stats.hitRate = totalReqs > 0 ? (this.stats.hits / totalReqs) * 100 : 0.0;
    this.stats.missRate = totalReqs > 0 ? (this.stats.misses / totalReqs) * 100 : 0.0;

    return { ...this.stats };
  }

  private getDefaultTtl(objectType: CacheObjectType): number {
    switch (objectType) {
      case CacheObjectType.DOCUMENT_PARSE:
      case CacheObjectType.DOCUMENT_CHUNK:
      case CacheObjectType.EMBEDDING:
        return 86400 * 7; // 7 days
      case CacheObjectType.SUMMARY:
      case CacheObjectType.RESEARCH:
        return 3600 * 24; // 24 hours
      case CacheObjectType.RETRIEVAL:
        return 3600 * 2;  // 2 hours
      case CacheObjectType.CONTEXT:
      case CacheObjectType.AGENT_DISCOVERY:
      default:
        return 300;       // 5 minutes
    }
  }

  private recordHit(): void {
    this.stats.hits++;
  }

  private recordMiss(): void {
    this.stats.misses++;
  }
}

// Global singleton instance
export const knowledgeCache = new KnowledgeCache();
