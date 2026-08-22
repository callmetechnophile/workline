/**
 * Document and Docling structural schemas.
 */

export enum SourceType {
  UPLOAD = "UPLOAD",
  PDF = "PDF",
  DATASHEET = "DATASHEET",
  RESEARCH_PAPER = "RESEARCH_PAPER",
  WEB = "WEB",
  GITHUB = "GITHUB",
  GIT = "GIT",
  WLIPJT = "WLIPJT",
  GENERATED = "GENERATED",
  OTHER = "OTHER",
}

export enum DocumentStatus {
  DISCOVERED = "DISCOVERED",
  INGESTING = "INGESTING",
  PARSED = "PARSED",
  ENRICHED = "ENRICHED",
  INDEXED = "INDEXED",
  FAILED = "FAILED",
  STALE = "STALE",
}

export interface TableCell {
  rowIndex: number;
  colIndex: number;
  text: string;
  isHeader?: boolean;
}

export interface TableElement {
  tableId: string;
  documentId: string;
  pageNumber: number;
  sectionTitle: string;
  headers: string[];
  rows: string[][];
  caption?: string;
}

export interface FigureElement {
  figureId: string;
  documentId: string;
  pageNumber: number;
  sectionTitle: string;
  caption?: string;
  artifactReference?: string;
}

export interface SectionElement {
  sectionId: string;
  heading: string;
  level: number;
  pageNumber: number;
  paragraphs: string[];
  tables: TableElement[];
  figures: FigureElement[];
}

export interface StructuredDocument {
  documentId: string;
  projectId: string;
  teamId: string;
  sourceType: SourceType;
  sourceUri: string;
  filename: string;
  mimeType: string;
  title: string;
  sourceHash: string;
  contentHash: string;
  createdAt: number;
  updatedAt: number;
  parser: string;
  parserVersion: string;
  status: DocumentStatus;
  sections: SectionElement[];
  metadata: Record<string, any>;
}
