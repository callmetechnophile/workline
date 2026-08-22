/**
 * LlamaIndex Node builder with section-aware chunking and page provenance.
 */

import { SectionElement, StructuredDocument } from "../docling/schemas";

export enum NodeType {
  DOCUMENT = "DOCUMENT",
  SECTION = "SECTION",
  PARAGRAPH = "PARAGRAPH",
  TABLE = "TABLE",
  FIGURE = "FIGURE",
  LIST = "LIST",
  ENTITY_CONTEXT = "ENTITY_CONTEXT",
}

export interface DocumentNode {
  nodeId: string;
  documentId: string;
  projectId: string;
  teamId: string;
  nodeType: NodeType;
  content: string;
  pageNumber: number;
  section: string;
  sourceHash: string;
  metadata: Record<string, any>;
}

export class LlamaIndexNodeBuilder {
  public static buildNodes(doc: StructuredDocument): DocumentNode[] {
    const nodes: DocumentNode[] = [];
    let counter = 1;

    for (const section of doc.sections) {
      // 1. Paragraph / Section text nodes
      for (const p of section.paragraphs) {
        nodes.push({
          nodeId: `${doc.documentId}_node_${counter++}`,
          documentId: doc.documentId,
          projectId: doc.projectId,
          teamId: doc.teamId,
          nodeType: NodeType.PARAGRAPH,
          content: `${section.heading}: ${p}`,
          pageNumber: section.pageNumber,
          section: section.heading,
          sourceHash: doc.sourceHash,
          metadata: {
            title: doc.title,
            filename: doc.filename,
            sourceType: doc.sourceType,
          },
        });
      }

      // 2. Structured Table nodes
      for (const t of section.tables) {
        const tableSummary = `Table: ${t.caption || section.heading}\nHeaders: ${t.headers.join(" | ")}\n` +
          t.rows.map((r) => r.join(" | ")).join("\n");

        nodes.push({
          nodeId: `${doc.documentId}_node_${counter++}`,
          documentId: doc.documentId,
          projectId: doc.projectId,
          teamId: doc.teamId,
          nodeType: NodeType.TABLE,
          content: tableSummary,
          pageNumber: t.pageNumber,
          section: section.heading,
          sourceHash: doc.sourceHash,
          metadata: {
            tableId: t.tableId,
            headers: t.headers,
            rowCount: t.rows.length,
          },
        });
      }
    }

    return nodes;
  }
}
