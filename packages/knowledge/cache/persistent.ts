/**
 * L2 Persistent File-System Cache under .workline/cache/
 */

import * as fs from "fs";
import * as path from "path";
import { CacheEntry, CacheObjectType } from "./metadata";
import { CacheSerializer } from "./serializer";

export class PersistentCache {
  private readonly baseDir: string;
  private readonly maxSizeBytes: number;

  constructor(baseDir: string = ".workline/cache", maxSizeBytes: number = 512 * 1024 * 1024) {
    this.baseDir = baseDir;
    this.maxSizeBytes = maxSizeBytes;
    this.ensureDirectoryStructure();
  }

  private ensureDirectoryStructure(): void {
    const subdirs = ["metadata", "documents", "embeddings", "retrieval", "context", "summaries"];
    for (const sub of subdirs) {
      const p = path.join(this.baseDir, sub);
      if (!fs.existsSync(p)) {
        fs.mkdirSync(p, { recursive: true });
      }
    }
  }

  private getFilePath(key: string, objectType: CacheObjectType): string {
    const safeKey = key.replace(/[^a-zA-Z0-9_-]/g, "_");
    let folder = "metadata";
    switch (objectType) {
      case CacheObjectType.DOCUMENT_PARSE:
      case CacheObjectType.DOCUMENT_CHUNK:
        folder = "documents";
        break;
      case CacheObjectType.EMBEDDING:
        folder = "embeddings";
        break;
      case CacheObjectType.RETRIEVAL:
        folder = "retrieval";
        break;
      case CacheObjectType.CONTEXT:
        folder = "context";
        break;
      case CacheObjectType.SUMMARY:
        folder = "summaries";
        break;
    }
    return path.join(this.baseDir, folder, `${safeKey}.json`);
  }

  public get<T>(key: string, objectType: CacheObjectType): CacheEntry<T> | null {
    try {
      const filePath = this.getFilePath(key, objectType);
      if (!fs.existsSync(filePath)) return null;

      const content = fs.readFileSync(filePath, "utf-8");
      const entry = CacheSerializer.deserialize<T>(content);
      if (!entry) {
        // Discard corrupted entry
        this.delete(key, objectType);
        return null;
      }

      // Check TTL expiration
      if (entry.metadata.expiresAt > 0 && Date.now() > entry.metadata.expiresAt) {
        this.delete(key, objectType);
        return null;
      }

      return entry;
    } catch {
      return null;
    }
  }

  public set<T>(entry: CacheEntry<T>): void {
    try {
      const filePath = this.getFilePath(entry.metadata.cacheKey, entry.metadata.objectType);
      const serialized = CacheSerializer.serialize(entry);
      fs.writeFileSync(filePath, serialized, "utf-8");
    } catch {
      // Graceful fallback on disk write failure
    }
  }

  public delete(key: string, objectType: CacheObjectType): boolean {
    try {
      const filePath = this.getFilePath(key, objectType);
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  public clear(): void {
    try {
      if (fs.existsSync(this.baseDir)) {
        fs.rmSync(this.baseDir, { recursive: true, force: true });
        this.ensureDirectoryStructure();
      }
    } catch {}
  }

  public getStats(): { totalEntries: number; totalSizeBytes: number } {
    let totalEntries = 0;
    let totalSizeBytes = 0;

    const countDir = (dir: string) => {
      if (!fs.existsSync(dir)) return;
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
          countDir(fullPath);
        } else if (stat.isFile() && item.endsWith(".json")) {
          totalEntries++;
          totalSizeBytes += stat.size;
        }
      }
    };

    countDir(this.baseDir);
    return { totalEntries, totalSizeBytes };
  }
}
