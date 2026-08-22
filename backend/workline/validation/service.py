"""Validation Service orchestrating candidate discovery, deterministic evaluation, and cache management."""

import hashlib
import threading
import time
from typing import Any, Dict, List, Optional
from backend.workline.knowledge.cache.cache import knowledge_cache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions
from backend.workline.knowledge.graph.service import knowledge_graph_service
from backend.workline.validation.evaluator import DeterministicConstraintEvaluator
from backend.workline.validation.models import (
    ConstraintOperator,
    ConstraintResult,
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
    ValidationResult,
    ValidationStatus,
)


class ValidationService:
    """Enterprise Engineering Requirement and Validation Service."""

    def __init__(self):
        self._lock = threading.RLock()
        self._requirements: Dict[str, EngineeringRequirement] = {}
        self._validations: Dict[str, ValidationResult] = {}
        self._rule_version = "electrical_rules_v1"

    def set_rule_version(self, version: str) -> None:
        with self._lock:
            self._rule_version = version

    def get_rule_version(self) -> str:
        with self._lock:
            return self._rule_version

    def create_requirement(
        self,
        requirement_id: str,
        project_id: str,
        description: str,
        category: RequirementCategory = RequirementCategory.ELECTRICAL,
        constraints: Optional[List[EngineeringConstraint]] = None,
        priority: str = "HIGH",
        team_id: str = "default_team",
    ) -> EngineeringRequirement:
        with self._lock:
            req = EngineeringRequirement(
                requirement_id=requirement_id,
                project_id=project_id,
                team_id=team_id,
                category=category,
                description=description,
                constraints=constraints or [],
                priority=priority,
                status="ACTIVE",
                created_at=time.time(),
                updated_at=time.time(),
            )
            self._requirements[requirement_id] = req
            return req

    def get_requirement(self, requirement_id: str) -> Optional[EngineeringRequirement]:
        with self._lock:
            return self._requirements.get(requirement_id)

    def list_requirements(self, project_id: Optional[str] = None) -> List[EngineeringRequirement]:
        with self._lock:
            if project_id:
                return [r for r in self._requirements.values() if r.project_id == project_id]
            return list(self._requirements.values())

    def validate_candidate(
        self,
        requirement_id: str,
        candidate_component_id: str,
    ) -> ValidationResult:
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                raise ValueError(f"Requirement '{requirement_id}' not found.")

            # Check cache
            cache_key = f"workline:val:{requirement_id}:{candidate_component_id}:{self._rule_version}"
            cached_val = knowledge_cache.get(cache_key, CacheObjectType.CONTEXT)
            if cached_val:
                return ValidationResult.model_validate(cached_val)

            # Retrieve candidate specifications from Knowledge Graph
            specs = knowledge_graph_service.get_specifications(candidate_component_id)
            conflicts = knowledge_graph_service.list_conflicts()
            candidate_conflicts = [c for c in conflicts if c.entity_id == candidate_component_id]

            constraint_results: List[ConstraintResult] = []
            has_fail = False
            has_unknown = False
            has_conflict = len(candidate_conflicts) > 0

            # Group candidate specifications by property
            spec_map: Dict[str, Any] = {}
            for s in specs:
                prop_key = s.property.lower().replace(" ", "_")
                spec_map[prop_key] = s

            conflict_props = {c.property.lower().replace(" ", "_"): c for c in candidate_conflicts}

            for c in req.constraints:
                prop_key = c.property.lower().replace(" ", "_")

                if prop_key in conflict_props:
                    conf = conflict_props[prop_key]
                    constraint_results.append(
                        ConstraintResult(
                            constraint_id=c.constraint_id,
                            property=c.property,
                            required_value=f"{c.operator.value} {c.required_value}",
                            actual_value=f"{conf.value_a} vs {conf.value_b}",
                            operator=c.operator.value,
                            status=ValidationStatus.CONFLICT,
                            reason=f"Conflicting specifications detected across documents ({conf.value_a} vs {conf.value_b})",
                        )
                    )
                    has_conflict = True
                    continue

                spec = spec_map.get(prop_key)

                if not spec:
                    constraint_results.append(
                        ConstraintResult(
                            constraint_id=c.constraint_id,
                            property=c.property,
                            required_value=f"{c.operator.value} {c.required_value}",
                            actual_value="UNKNOWN",
                            operator=c.operator.value,
                            status=ValidationStatus.UNKNOWN,
                            reason=f"No specification found for property '{c.property}' in candidate documentation",
                        )
                    )
                    has_unknown = True
                    continue

                outcome = DeterministicConstraintEvaluator.evaluate(
                    constraint=c,
                    actual_val=spec.normalized_value,
                    actual_unit=spec.unit,
                )

                constraint_results.append(
                    ConstraintResult(
                        constraint_id=c.constraint_id,
                        property=c.property,
                        required_value=f"{c.operator.value} {c.required_value}",
                        actual_value=spec.value,
                        operator=c.operator.value,
                        status=outcome.status,
                        unit=spec.unit,
                        source_document=spec.source_document,
                        page=spec.page,
                        section=spec.section,
                        reason=outcome.reason,
                    )
                )

                if outcome.status == ValidationStatus.FAIL:
                    has_fail = True
                elif outcome.status == ValidationStatus.UNKNOWN:
                    has_unknown = True

            overall = ValidationStatus.PASS
            if has_conflict:
                overall = ValidationStatus.CONFLICT
            elif has_fail:
                overall = ValidationStatus.FAIL
            elif has_unknown:
                overall = ValidationStatus.UNKNOWN

            val_id = f"VAL-{candidate_component_id}-{int(time.time() * 1000)}"
            result = ValidationResult(
                validation_id=val_id,
                candidate_id=candidate_component_id,
                requirement_id=requirement_id,
                overall_status=overall,
                constraint_results=constraint_results,
                conflicts=[f"{c.property}: {c.value_a} vs {c.value_b}" for c in candidate_conflicts],
                warnings=[],
                rule_version=self._rule_version,
                knowledge_version="1.0.0",
                created_at=time.time(),
            )

            self._validations[val_id] = result

            # Save in Knowledge Cache
            knowledge_cache.set(
                cache_key,
                result.model_dump(),
                CacheObjectType.CONTEXT,
                CacheOptions(
                    project_id=req.project_id,
                    source_id=requirement_id,
                ),
            )

            return result

    def get_validation(self, validation_id: str) -> Optional[ValidationResult]:
        with self._lock:
            return self._validations.get(validation_id)


# Global singleton instance
validation_service = ValidationService()
