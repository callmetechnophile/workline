/**
 * Unified LlamaIndex client coordinating ingestion, embeddings, indexing, retrieval, and context building behind caching.
 */

import { CachedEmbeddingService } from "./embeddings";
import { CachedIngestionPipeline, DocumentChunk, ParsedDocument } from "./ingestion";
import { CachedIndexingManager } from "./indexing";
import { CachedRetrievalPipeline, RetrievedCandidate } from "./retrieval";
import { CachedContextBuilder } from "./context";

export class LlamaIndexKnowledgeClient {
  public embeddings: CachedEmbeddingService;
  public ingestion: CachedIngestionPipeline;
  public indexing: CachedIndexingManager;
  public retrieval: CachedRetrievalPipeline;
  public context: CachedContextBuilder;

  constructor() {
    this.embeddings = new CachedEmbeddingService();
    this.ingestion = new CachedIngestionPipeline();
    this.indexing = new CachedIndexingManager();
    this.retrieval = new CachedRetrievalPipeline();
    this.context = new CachedContextBuilder();
  }

  public async ingestAndIndex(docId: string, content: string, projectId: string): Promise<DocumentChunk[]> {
    const parsed = await this.ingestion.parseDocument(docId, content, projectId);
    const chunks = await this.ingestion.chunkDocument(parsed, projectId);

    for (const chunk of chunks) {
      await this.embeddings.getEmbedding(chunk.content, projectId);
    }

    this.indexing.incrementIndexVersion(projectId);
    return chunks;
  }

  public async queryContext(
    projectId: string,
    query: string,
    knowledgeVersion: number = 1,
    authoritativeStatusMap?: Map<string, string>
  ): Promise<string> {
    const indexVersion = this.indexing.getIndexVersion(projectId);
    const candidates = await this.retrieval.retrieve(projectId, query, indexVersion, authoritativeStatusMap);
    return await this.context.buildContext(projectId, query, knowledgeVersion, candidates);
  }
}

export const llamaIndexClient = new LlamaIndexKnowledgeClient();
