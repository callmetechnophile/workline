/**
 * Cached document parsing and chunking ingestion pipeline.
 */

import { knowledgeCache } from "../cache/cache";
import { CacheKeyGenerator } from "../cache/keys";
import { CacheObjectType } from "../cache/metadata";

export interface ParsedDocument {
  docId: string;
  sourceHash: string;
  title: string;
  sections: Array<{ heading: string; body: string }>;
}

export interface DocumentChunk {
  chunkId: string;
  docId: string;
  content: string;
  contentHash: string;
}

export class CachedIngestionPipeline {
  public async parseDocument(docId: string, rawContent: string, projectId: string): Promise<ParsedDocument> {
    const sourceHash = CacheKeyGenerator.hash(rawContent);
    const cacheKey = CacheKeyGenerator.generateKey(CacheObjectType.DOCUMENT_PARSE, projectId, docId, sourceHash);

    // 1. Cache lookup
    const cached = await knowledgeCache.get<ParsedDocument>(cacheKey, CacheObjectType.DOCUMENT_PARSE);
    if (cached && cached.sourceHash === sourceHash) {
      return cached;
    }

    // 2. Parse document
    const parsed: ParsedDocument = {
      docId,
      sourceHash,
      title: `Doc: ${docId}`,
      sections: rawContent.split("\n\n").map((part, idx) => ({
        heading: `Section ${idx + 1}`,
        body: part.trim(),
      })),
    };

    // 3. Cache
    await knowledgeCache.set(cacheKey, parsed, CacheObjectType.DOCUMENT_PARSE, {
      projectId,
      sourceId: docId,
      sourceHash,
    });

    return parsed;
  }

  public async chunkDocument(parsed: ParsedDocument, projectId: string): Promise<DocumentChunk[]> {
    const cacheKey = CacheKeyGenerator.generateKey(CacheObjectType.DOCUMENT_CHUNK, projectId, parsed.docId, parsed.sourceHash);

    // 1. Cache lookup
    const cached = await knowledgeCache.get<DocumentChunk[]>(cacheKey, CacheObjectType.DOCUMENT_CHUNK);
    if (cached) {
      return cached;
    }

    // 2. Chunking
    const chunks: DocumentChunk[] = parsed.sections.map((sec, idx) => ({
      chunkId: `${parsed.docId}_chunk_${idx}`,
      docId: parsed.docId,
      content: `${sec.heading}\n${sec.body}`,
      contentHash: CacheKeyGenerator.hash(`${sec.heading}\n${sec.body}`),
    }));

    // 3. Cache
    await knowledgeCache.set(cacheKey, chunks, CacheObjectType.DOCUMENT_CHUNK, {
      projectId,
      sourceId: parsed.docId,
      sourceHash: parsed.sourceHash,
    });

    return chunks;
  }
}
