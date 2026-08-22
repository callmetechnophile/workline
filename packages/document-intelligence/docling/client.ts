/**
 * Docling Client interface.
 */

import { DoclingParser } from "./parser";
import { SourceType, StructuredDocument } from "./schemas";

export class DoclingClient {
  public async parseDocument(
    documentId: string,
    projectId: string,
    content: string,
    filename: string,
    sourceType: SourceType = SourceType.DATASHEET,
    sourceHash: string = "hash"
  ): Promise<StructuredDocument> {
    return DoclingParser.parse(documentId, projectId, content, filename, sourceType, sourceHash);
  }
}

export const doclingClient = new DoclingClient();
