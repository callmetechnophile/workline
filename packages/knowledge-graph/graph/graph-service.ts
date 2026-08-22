/**
 * Knowledge Graph query and coordination service with bounded depth traversal.
 */

import { CanonicalEntity, EntityMention, Specification, SpecificationConflict } from "../entities/entity-schema";
import { EngineeringRelationship, RelationshipType } from "../relationships/relationship-types";
import { EntityResolver } from "../entities/entity-resolver";
import { ConflictDetector } from "../validation/conflict-detection";

export interface GraphQueryResult {
  entity: CanonicalEntity;
  specifications: Specification[];
  relationships: EngineeringRelationship[];
  conflicts: SpecificationConflict[];
  relatedEntities: CanonicalEntity[];
}

export class KnowledgeGraphService {
  private entities = new Map<string, CanonicalEntity>();
  private specifications = new Map<string, Specification[]>();
  private relationships: EngineeringRelationship[] = [];
  private conflicts: SpecificationConflict[] = [];

  public addEntity(entity: CanonicalEntity): void {
    this.entities.set(entity.entityId, entity);
  }

  public getEntity(entityId: string): CanonicalEntity | undefined {
    return this.entities.get(entityId);
  }

  public addSpecification(spec: Specification): void {
    if (!this.specifications.has(spec.entityId)) {
      this.specifications.set(spec.entityId, []);
    }
    this.specifications.get(spec.entityId)!.push(spec);

    // Run conflict detection on the entity's specifications
    const updatedConflicts = ConflictDetector.detectConflicts(this.specifications.get(spec.entityId)!);
    this.conflicts = this.conflicts.filter((c) => c.entityId !== spec.entityId).concat(updatedConflicts);
  }

  public addRelationship(rel: EngineeringRelationship): void {
    this.relationships.push(rel);
  }

  public queryEntityGraph(entityId: string, maxDepth: number = 2): GraphQueryResult | null {
    const entity = this.entities.get(entityId);
    if (!entity) return null;

    const specs = this.specifications.get(entityId) || [];
    const directRels = this.relationships.filter(
      (r) => (r.fromEntity === entityId || r.toEntity === entityId) && r.status === "ACTIVE"
    );

    const relatedIds = new Set<string>();
    for (const r of directRels) {
      if (r.fromEntity !== entityId) relatedIds.add(r.fromEntity);
      if (r.toEntity !== entityId) relatedIds.add(r.toEntity);
    }

    const relatedEntities: CanonicalEntity[] = [];
    for (const rid of relatedIds) {
      const e = this.entities.get(rid);
      if (e) relatedEntities.push(e);
    }

    const entityConflicts = this.conflicts.filter((c) => c.entityId === entityId);

    return {
      entity,
      specifications: specs,
      relationships: directRels,
      conflicts: entityConflicts,
      relatedEntities,
    };
  }

  public getConflicts(projectId?: string): SpecificationConflict[] {
    return this.conflicts;
  }
}

export const knowledgeGraphService = new KnowledgeGraphService();
