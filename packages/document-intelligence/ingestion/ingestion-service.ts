/**
 * Document Ingestion Service orchestrating Docling, spaCy, LlamaIndex, and KnowledgeCache.
 */

import { doclingClient } from "../docling/client";
import { spacyClient } from "../spacy/client";
import { LlamaIndexNodeBuilder, DocumentNode } from "../llamaindex/node-builder";
import { SourceType, StructuredDocument, DocumentStatus } from "../docling/schemas";
import { EngineeringEntity } from "../entities/engineering-entities";

export interface IngestionResult {
  document: StructuredDocument;
  entities: EngineeringEntity[];
  nodes: DocumentNode[];
}

export class DocumentIngestionService {
  public async ingest(
    documentId: string,
    projectId: string,
    rawContent: string,
    filename: string,
    sourceType: SourceType = SourceType.DATASHEET
  ): Promise<IngestionResult> {
    // 1. Docling structural parsing
    const document = await doclingClient.parseDocument(
      documentId,
      projectId,
      rawContent,
      filename,
      sourceType,
      "sha256_mock_hash"
    );

    // 2. spaCy linguistic enrichment & entity extraction
    const { entities } = spacyClient.enrich(document);
    document.status = DocumentStatus.ENRICHED;

    // 3. LlamaIndex node creation with section-aware chunking
    const nodes = LlamaIndexNodeBuilder.buildNodes(document);
    document.status = DocumentStatus.INDEXED;

    return {
      document,
      entities,
      nodes,
    };
  }
}

export const documentIngestionService = new DocumentIngestionService();
