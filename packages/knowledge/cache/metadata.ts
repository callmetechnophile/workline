/**
 * Cache object types, metadata models, and options.
 */

export enum CacheObjectType {
  DOCUMENT_PARSE = "DOCUMENT_PARSE",
  DOCUMENT_CHUNK = "DOCUMENT_CHUNK",
  EMBEDDING = "EMBEDDING",
  RETRIEVAL = "RETRIEVAL",
  CONTEXT = "CONTEXT",
  SUMMARY = "SUMMARY",
  RESEARCH = "RESEARCH",
  AGENT_DISCOVERY = "AGENT_DISCOVERY",
}

export interface CacheOptions {
  ttl?: number; // Time-to-live in seconds
  projectId: string;
  teamId?: string;
  sourceId?: string;
  sourceHash?: string;
  schemaVersion?: string;
  projectVersion?: string;
  gitCommit?: string;
  provider?: string;
  model?: string;
  embeddingDimension?: number;
  metadata?: Record<string, any>;
}

export interface CacheMetadata {
  cacheKey: string;
  objectType: CacheObjectType;
  projectId: string;
  teamId: string;
  sourceId?: string;
  sourceHash?: string;
  schemaVersion: string;
  createdAt: number; // Unix timestamp in ms
  expiresAt: number; // Unix timestamp in ms (0 if infinite)
  projectVersion?: string;
  gitCommit?: string;
  provider?: string;
  model?: string;
  embeddingDimension?: number;
  sizeBytes: number;
}

export interface CacheEntry<T = any> {
  metadata: CacheMetadata;
  data: T;
}

export interface CacheStats {
  hits: number;
  misses: number;
  evictions: number;
  expired: number;
  invalidations: number;
  l1Entries: number;
  l2Entries: number;
  l2SizeBytes: number;
  hitRate: number;
  missRate: number;
}
