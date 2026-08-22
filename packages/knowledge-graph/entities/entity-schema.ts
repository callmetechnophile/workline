/**
 * Canonical Entity, Mention, Specification, and Conflict schemas.
 */

import { EntityStatus, EntityType } from "./entity-types";

export interface CanonicalEntity {
  entityId: string;
  entityType: EntityType;
  canonicalName: string;
  aliases: string[];
  normalizedName: string;
  projectId: string;
  teamId: string;
  status: EntityStatus;
  confidence: number;
  manufacturer?: string;
  basePartNumber?: string;
  packageVariant?: string;
  createdAt: number;
  updatedAt: number;
  metadata?: Record<string, any>;
}

export interface EntityMention {
  mentionId: string;
  documentId: string;
  pageNumber: number;
  sectionId: string;
  entityType: EntityType;
  originalText: string;
  normalizedText: string;
  sourceSpan: string;
  confidence: number;
  contextHints?: Record<string, any>;
}

export interface Specification {
  specificationId: string;
  entityId: string;
  property: string;
  value: string;
  normalizedValue: number;
  unit: string;
  sourceDocument: string;
  page: number;
  section: string;
  confidence: number;
  validFrom?: number;
  validUntil?: number;
  status: EntityStatus;
}

export interface SpecificationConflict {
  conflictId: string;
  entityId: string;
  property: string;
  valueA: string;
  sourceA: string;
  valueB: string;
  sourceB: string;
  status: "OPEN" | "RESOLVED" | "ACKNOWLEDGED";
  createdAt: number;
}
