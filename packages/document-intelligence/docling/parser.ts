/**
 * Docling document structure parser.
 */

import {
  DocumentStatus,
  SectionElement,
  SourceType,
  StructuredDocument,
  TableElement,
} from "./schemas";
import { DoclingNormalization } from "./normalization";

export class DoclingParser {
  public static parse(
    documentId: string,
    projectId: string,
    rawContent: string,
    filename: string,
    sourceType: SourceType = SourceType.DATASHEET,
    sourceHash: string = "hash"
  ): StructuredDocument {
    const lines = rawContent.split("\n");
    const sections: SectionElement[] = [];
    let currentSection: SectionElement = {
      sectionId: `${documentId}_sec_0`,
      heading: "General Overview",
      level: 1,
      pageNumber: 1,
      paragraphs: [],
      tables: [],
      figures: [],
    };

    let paragraphBuffer: string[] = [];
    let page = 1;

    for (let i = 0; i < lines.length; i++) {
      const line = DoclingNormalization.cleanText(lines[i]);
      if (!line) {
        if (paragraphBuffer.length > 0) {
          currentSection.paragraphs.push(paragraphBuffer.join(" "));
          paragraphBuffer = [];
        }
        continue;
      }

      if (line.startsWith("Page ") || line.startsWith("--- Page")) {
        page++;
        continue;
      }

      // Check table pattern (e.g. | Col1 | Col2 |)
      if (line.startsWith("|") && line.endsWith("|")) {
        if (paragraphBuffer.length > 0) {
          currentSection.paragraphs.push(paragraphBuffer.join(" "));
          paragraphBuffer = [];
        }

        const tableRows: string[][] = [];
        while (i < lines.length && lines[i].trim().startsWith("|")) {
          const rowLine = lines[i].trim();
          if (!rowLine.includes("---")) {
            const cols = rowLine
              .split("|")
              .slice(1, -1)
              .map((c) => c.trim());
            tableRows.push(cols);
          }
          i++;
        }
        i--; // Adjust loop

        if (tableRows.length > 0) {
          const tableElem: TableElement = {
            tableId: `${documentId}_tbl_${currentSection.tables.length + 1}`,
            documentId,
            pageNumber: page,
            sectionTitle: currentSection.heading,
            headers: tableRows[0] || [],
            rows: tableRows.slice(1),
            caption: `Table in ${currentSection.heading}`,
          };
          currentSection.tables.push(tableElem);
        }
        continue;
      }

      // Heading detection
      if (line.startsWith("#") || line.toUpperCase() === line && line.length < 50 && line.length > 3) {
        if (paragraphBuffer.length > 0) {
          currentSection.paragraphs.push(paragraphBuffer.join(" "));
          paragraphBuffer = [];
        }
        if (currentSection.paragraphs.length > 0 || currentSection.tables.length > 0) {
          sections.push(currentSection);
        }

        const headingText = line.replace(/^#+\s*/, "");
        currentSection = {
          sectionId: `${documentId}_sec_${sections.length + 1}`,
          heading: headingText,
          level: line.startsWith("##") ? 2 : 1,
          pageNumber: page,
          paragraphs: [],
          tables: [],
          figures: [],
        };
        continue;
      }

      paragraphBuffer.push(line);
    }

    if (paragraphBuffer.length > 0) {
      currentSection.paragraphs.push(paragraphBuffer.join(" "));
    }
    sections.push(currentSection);

    return {
      documentId,
      projectId,
      teamId: "default_team",
      sourceType,
      sourceUri: `file://${filename}`,
      filename,
      mimeType: filename.endsWith(".pdf") ? "application/pdf" : "text/markdown",
      title: sections[0]?.heading || filename,
      sourceHash,
      contentHash: sourceHash,
      createdAt: Date.now(),
      updatedAt: Date.now(),
      parser: "DoclingParser",
      parserVersion: "2.1.0",
      status: DocumentStatus.PARSED,
      sections,
      metadata: { pageCount: page },
    };
  }
}
