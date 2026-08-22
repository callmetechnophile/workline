/**
 * L1 Bounded In-Memory Cache with LRU eviction and TTL support.
 */

import { CacheEntry } from "./metadata";

export class MemoryCache {
  private map: Map<string, CacheEntry>;
  private readonly maxEntries: number;

  constructor(maxEntries: number = 1000) {
    this.maxEntries = maxEntries;
    this.map = new Map<string, CacheEntry>();
  }

  public get<T>(key: string): CacheEntry<T> | null {
    const entry = this.map.get(key);
    if (!entry) return null;

    // Check expiration
    if (entry.metadata.expiresAt > 0 && Date.now() > entry.metadata.expiresAt) {
      this.map.delete(key);
      return null;
    }

    // Refresh LRU order (delete & re-insert)
    this.map.delete(key);
    this.map.set(key, entry);

    return entry as CacheEntry<T>;
  }

  public set<T>(entry: CacheEntry<T>): void {
    const key = entry.metadata.cacheKey;
    if (this.map.has(key)) {
      this.map.delete(key);
    } else if (this.map.size >= this.maxEntries) {
      // Evict oldest entry
      const oldestKey = this.map.keys().next().value;
      if (oldestKey) {
        this.map.delete(oldestKey);
      }
    }
    this.map.set(key, entry);
  }

  public has(key: string): boolean {
    return this.get(key) !== null;
  }

  public delete(key: string): boolean {
    return this.map.delete(key);
  }

  public clear(): void {
    this.map.clear();
  }

  public size(): number {
    return this.map.size;
  }

  public entries(): CacheEntry[] {
    return Array.from(this.map.values());
  }

  public clearExpired(): number {
    const now = Date.now();
    let count = 0;
    for (const [key, entry] of this.map.entries()) {
      if (entry.metadata.expiresAt > 0 && now > entry.metadata.expiresAt) {
        this.map.delete(key);
        count++;
      }
    }
    return count;
  }
}
