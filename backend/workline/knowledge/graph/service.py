"""Knowledge Graph Service managing canonical entities, relationships, specifications, conflicts, and hybrid queries."""

import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions
from backend.workline.knowledge.graph.models import (
    CanonicalEntity,
    EngineeringRelationship,
    EntityMention,
    EntityStatus,
    EntityType,
    RelationshipType,
    Specification,
    SpecificationConflict,
)
from backend.workline.knowledge.graph.normalizer import EntityNormalizer
from backend.workline.knowledge.graph.resolver import EntityResolver, ResolutionResult


class KnowledgeGraphService:
    """Enterprise Engineering Knowledge Graph service."""

    def __init__(self):
        self._lock = threading.RLock()
        self._entities: Dict[str, CanonicalEntity] = {}
        self._specifications: Dict[str, List[Specification]] = {}
        self._relationships: List[EngineeringRelationship] = []
        self._conflicts: Dict[str, SpecificationConflict] = {}

    def create_entity(
        self,
        entity_id: str,
        entity_type: EntityType,
        canonical_name: str,
        project_id: str,
        team_id: str = "default_team",
        manufacturer: Optional[str] = None,
        base_part_number: Optional[str] = None,
        package_variant: Optional[str] = None,
        aliases: Optional[List[str]] = None,
    ) -> CanonicalEntity:
        with self._lock:
            entity = CanonicalEntity(
                entity_id=entity_id,
                entity_type=entity_type,
                canonical_name=canonical_name,
                aliases=aliases or [],
                normalized_name=canonical_name.strip().upper(),
                project_id=project_id,
                team_id=team_id,
                status=EntityStatus.ACTIVE,
                confidence=1.0,
                manufacturer=manufacturer,
                base_part_number=base_part_number,
                package_variant=package_variant,
                created_at=time.time(),
                updated_at=time.time(),
            )
            self._entities[entity_id] = entity
            # Invalidate project graph cache
            knowledge_cache.invalidate_by_project(project_id)
            return entity

    def get_entity(self, entity_id: str) -> Optional[CanonicalEntity]:
        with self._lock:
            return self._entities.get(entity_id)

    def search_entities(
        self,
        query: str,
        project_id: Optional[str] = None,
        entity_type: Optional[EntityType] = None,
    ) -> List[CanonicalEntity]:
        with self._lock:
            q = query.strip().upper()
            results = []
            for e in self._entities.values():
                if project_id and e.project_id != project_id:
                    continue
                if entity_type and e.entity_type != entity_type:
                    continue
                if q in e.canonical_name.upper() or any(q in a.upper() for a in e.aliases):
                    results.append(e)
            return results

    def add_specification(
        self,
        specification_id: str,
        entity_id: str,
        property_name: str,
        value_str: str,
        source_document: str,
        page: int = 1,
        section: str = "General",
        confidence: float = 0.95,
    ) -> Specification:
        with self._lock:
            parsed = EntityNormalizer.parse_quantity(value_str)
            norm_val = parsed.normalized_value if parsed else 0.0
            unit = parsed.base_unit if parsed else ""

            spec = Specification(
                specification_id=specification_id,
                entity_id=entity_id,
                property=property_name,
                value=value_str,
                normalized_value=norm_val,
                unit=unit,
                source_document=source_document,
                page=page,
                section=section,
                confidence=confidence,
                status=EntityStatus.ACTIVE,
            )

            if entity_id not in self._specifications:
                self._specifications[entity_id] = []

            # Check for conflict with existing specifications on the same property
            for existing in self._specifications[entity_id]:
                if existing.property.lower() == property_name.lower():
                    if abs(existing.normalized_value - norm_val) > 1e-5:
                        # Register conflict without overwriting
                        conflict_id = f"CONF-{entity_id}-{int(time.time() * 1000)}"
                        conflict = SpecificationConflict(
                            conflict_id=conflict_id,
                            entity_id=entity_id,
                            property=property_name,
                            value_a=existing.value,
                            source_a=f"{existing.source_document} (P.{existing.page})",
                            value_b=value_str,
                            source_b=f"{source_document} (P.{page})",
                            status="OPEN",
                        )
                        self._conflicts[conflict_id] = conflict

            self._specifications[entity_id].append(spec)
            return spec

    def get_specifications(self, entity_id: str) -> List[Specification]:
        with self._lock:
            return self._specifications.get(entity_id, [])

    def add_relationship(
        self,
        relationship_id: str,
        project_id: str,
        from_entity: str,
        relationship_type: RelationshipType,
        to_entity: str,
        source_type: str = "PROJECT_STATE",
        source_document: Optional[str] = None,
        source_span: Optional[str] = None,
    ) -> EngineeringRelationship:
        with self._lock:
            rel = EngineeringRelationship(
                relationship_id=relationship_id,
                project_id=project_id,
                from_entity=from_entity,
                relationship_type=relationship_type,
                to_entity=to_entity,
                confidence=1.0,
                source_type=source_type,
                source_document=source_document,
                source_span=source_span,
                created_at=time.time(),
                status="ACTIVE",
            )
            self._relationships.append(rel)
            knowledge_cache.invalidate_by_project(project_id)
            return rel

    def get_related(self, entity_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """Bounded depth graph traversal."""
        with self._lock:
            entity = self._entities.get(entity_id)
            if not entity:
                return {}

            direct_rels = [
                r for r in self._relationships
                if (r.from_entity == entity_id or r.to_entity == entity_id) and r.status == "ACTIVE"
            ]

            related_entities = []
            for r in direct_rels:
                target_id = r.to_entity if r.from_entity == entity_id else r.from_entity
                if target_id in self._entities:
                    related_entities.append(self._entities[target_id].model_dump())

            specs = [s.model_dump() for s in self._specifications.get(entity_id, [])]
            conflicts = [c.model_dump() for c in self._conflicts.values() if c.entity_id == entity_id]

            return {
                "entity": entity.model_dump(),
                "relationships": [r.model_dump() for r in direct_rels],
                "related_entities": related_entities,
                "specifications": specs,
                "conflicts": conflicts,
            }

    def list_conflicts(self, project_id: Optional[str] = None) -> List[SpecificationConflict]:
        with self._lock:
            return list(self._conflicts.values())

    def evaluate_requirement_candidate(
        self,
        component_entity_id: str,
        required_voltage: Optional[float] = None,
        min_current: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Deterministic numerical evaluation of component against engineering requirements."""
        with self._lock:
            specs = self._specifications.get(component_entity_id, [])
            results = {"component_id": component_entity_id, "satisfied": True, "details": []}

            if required_voltage is not None:
                v_spec = next((s for s in specs if "voltage" in s.property.lower() or "vout" in s.property.lower()), None)
                if v_spec:
                    match = abs(v_spec.normalized_value - required_voltage) < 0.05
                    results["details"].append({
                        "check": "voltage",
                        "required": f"{required_voltage} V",
                        "actual": v_spec.value,
                        "pass": match,
                    })
                    if not match:
                        results["satisfied"] = False
                else:
                    results["details"].append({"check": "voltage", "pass": False, "reason": "No voltage spec found"})
                    results["satisfied"] = False

            if min_current is not None:
                c_spec = next((s for s in specs if "current" in s.property.lower() or "iout" in s.property.lower()), None)
                if c_spec:
                    match = c_spec.normalized_value >= min_current
                    results["details"].append({
                        "check": "current",
                        "required": f">={min_current} A",
                        "actual": c_spec.value,
                        "pass": match,
                    })
                    if not match:
                        results["satisfied"] = False
                else:
                    results["details"].append({"check": "current", "pass": False, "reason": "No current spec found"})
                    results["satisfied"] = False

            return results


# Global singleton instance
knowledge_graph_service = KnowledgeGraphService()
