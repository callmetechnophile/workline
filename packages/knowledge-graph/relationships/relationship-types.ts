/**
 * Engineering Knowledge Graph Relationship Edge Types.
 */

export enum RelationshipType {
  // Project
  HAS_REQUIREMENT = "HAS_REQUIREMENT",
  HAS_COMPONENT = "HAS_COMPONENT",
  HAS_BOM_ITEM = "HAS_BOM_ITEM",
  HAS_DECISION = "HAS_DECISION",
  HAS_DOCUMENT = "HAS_DOCUMENT",

  // Document
  MENTIONS = "MENTIONS",
  REFERENCES = "REFERENCES",
  SUPPORTS = "SUPPORTS",
  CONTRADICTS = "CONTRADICTS",

  // Component
  MANUFACTURED_BY = "MANUFACTURED_BY",
  HAS_PART_NUMBER = "HAS_PART_NUMBER",
  HAS_DATASHEET = "HAS_DATASHEET",
  HAS_SPECIFICATION = "HAS_SPECIFICATION",
  HAS_ALIAS = "HAS_ALIAS",
  USED_IN = "USED_IN",

  // BOM
  REFERENCES_COMPONENT = "REFERENCES_COMPONENT",
  HAS_PROCUREMENT_ITEM = "HAS_PROCUREMENT_ITEM",

  // Requirement
  SATISFIED_BY = "SATISFIED_BY",
  SUPPORTED_BY = "SUPPORTED_BY",

  // Decision
  SELECTS = "SELECTS",
  REJECTS = "REJECTS",
  CONTRADICTED_BY = "CONTRADICTED_BY",

  // Procurement
  REPRESENTS = "REPRESENTS",
  SOLD_BY = "SOLD_BY",
}

export interface EngineeringRelationship {
  relationshipId: string;
  projectId: string;
  fromEntity: string;
  relationshipType: RelationshipType;
  toEntity: string;
  confidence: number;
  sourceType: "PROJECT_STATE" | "DOCUMENT_EVIDENCE" | "DETERMINISTIC_RULE" | "USER_CONFIRMATION";
  sourceDocument?: string;
  sourceSpan?: string;
  createdAt: number;
  status: "ACTIVE" | "DEPRECATED" | "SUPERSEDED";
}
