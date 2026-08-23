"""
Validation Service orchestrating candidate discovery, deterministic evaluation, requirement/constraint CRUD, and project summary metrics.
"""

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
    ConstraintSeverity,
    ConstraintStatus,
    EngineeringConstraint,
    EngineeringRequirement,
    RequirementCategory,
    RequirementOverviewSummary,
    RequirementPriority,
    RequirementStatus,
    ValidationResult,
    ValidationStatus,
)


class ValidationService:
    """Enterprise Engineering Requirement and Validation Service."""

    def __init__(self):
        self._lock = threading.RLock()
        self._requirements: Dict[str, EngineeringRequirement] = {}
        self._constraints: Dict[str, EngineeringConstraint] = {}
        self._validations: Dict[str, ValidationResult] = {}
        self._rule_version = "electrical_rules_v1"

    def set_rule_version(self, version: str) -> None:
        with self._lock:
            self._rule_version = version

    def get_rule_version(self) -> str:
        with self._lock:
            return self._rule_version

    # ==================== REQUIREMENT CRUD ====================

    def create_requirement(
        self,
        requirement_id: str,
        project_id: str,
        description: str,
        title: Optional[str] = None,
        category: RequirementCategory = RequirementCategory.ELECTRICAL,
        parameter: Optional[str] = None,
        target_value: Optional[str] = None,
        unit: Optional[str] = None,
        priority: RequirementPriority = RequirementPriority.HIGH,
        status: RequirementStatus = RequirementStatus.ACTIVE,
        verification_method: Optional[str] = "Simulation",
        source: Optional[str] = None,
        constraints: Optional[List[EngineeringConstraint]] = None,
        team_id: str = "default_team",
    ) -> EngineeringRequirement:
        with self._lock:
            req = EngineeringRequirement(
                requirement_id=requirement_id,
                project_id=project_id,
                title=title or description[:40],
                team_id=team_id,
                category=category,
                parameter=parameter,
                target_value=target_value,
                unit=unit,
                description=description,
                constraints=constraints or [],
                priority=priority,
                status=status,
                verification_method=verification_method,
                source=source,
                created_at=time.time(),
                updated_at=time.time(),
            )
            self._requirements[requirement_id] = req

            # If constraints were passed, store them in index
            for c in req.constraints:
                c.project_id = project_id
                c.requirement_id = requirement_id
                self._constraints[c.constraint_id] = c

            return req

    def update_requirement(
        self,
        requirement_id: str,
        updates: Dict[str, Any],
    ) -> Optional[EngineeringRequirement]:
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                return None

            data = req.model_dump()
            data.update(updates)
            data["updated_at"] = time.time()
            updated_req = EngineeringRequirement.model_validate(data)
            self._requirements[requirement_id] = updated_req
            return updated_req

    def delete_requirement(self, requirement_id: str) -> bool:
        with self._lock:
            if requirement_id in self._requirements:
                del self._requirements[requirement_id]
                # Also delete associated constraints
                to_del = [cid for cid, c in self._constraints.items() if c.requirement_id == requirement_id]
                for cid in to_del:
                    del self._constraints[cid]
                return True
            return False

    def get_requirement(self, requirement_id: str) -> Optional[EngineeringRequirement]:
        with self._lock:
            return self._requirements.get(requirement_id)

    def list_requirements(self, project_id: Optional[str] = None) -> List[EngineeringRequirement]:
        with self._lock:
            if project_id:
                return [r for r in self._requirements.values() if r.project_id == project_id]
            return list(self._requirements.values())

    # ==================== CONSTRAINT CRUD ====================

    def create_constraint(
        self,
        constraint_id: str,
        property_name: str,
        operator: ConstraintOperator,
        required_value: str,
        project_id: Optional[str] = None,
        requirement_id: Optional[str] = None,
        required_unit: Optional[str] = None,
        category: Optional[str] = "ELECTRICAL",
        severity: ConstraintSeverity = ConstraintSeverity.CRITICAL,
        verification_method: Optional[str] = "Simulation",
        source: Optional[str] = None,
    ) -> EngineeringConstraint:
        with self._lock:
            constraint = EngineeringConstraint(
                constraint_id=constraint_id,
                project_id=project_id,
                requirement_id=requirement_id,
                property=property_name,
                operator=operator,
                required_value=required_value,
                required_unit=required_unit,
                category=category,
                severity=severity,
                status=ConstraintStatus.ACTIVE,
                verification_method=verification_method,
                source=source,
                created_at=time.time(),
                updated_at=time.time(),
            )
            self._constraints[constraint_id] = constraint

            # If linked to a requirement, attach to that requirement
            if requirement_id and requirement_id in self._requirements:
                req = self._requirements[requirement_id]
                req.constraints = [c for c in req.constraints if c.constraint_id != constraint_id] + [constraint]
                req.updated_at = time.time()

            return constraint

    def delete_constraint(self, constraint_id: str) -> bool:
        with self._lock:
            if constraint_id in self._constraints:
                c = self._constraints[constraint_id]
                if c.requirement_id and c.requirement_id in self._requirements:
                    req = self._requirements[c.requirement_id]
                    req.constraints = [item for item in req.constraints if item.constraint_id != constraint_id]
                del self._constraints[constraint_id]
                return True
            return False

    def list_constraints(
        self,
        project_id: Optional[str] = None,
        requirement_id: Optional[str] = None,
    ) -> List[EngineeringConstraint]:
        with self._lock:
            results = list(self._constraints.values())
            if project_id:
                results = [c for c in results if c.project_id == project_id]
            if requirement_id:
                results = [c for c in results if c.requirement_id == requirement_id]
            return results

    # ==================== VALIDATION OVERVIEW ====================

    def get_project_validation_overview(self, project_id: str) -> RequirementOverviewSummary:
        """Calculates consolidated requirements & constraints metrics for a project."""
        with self._lock:
            reqs = [r for r in self._requirements.values() if r.project_id == project_id]
            constraints = [c for c in self._constraints.values() if c.project_id == project_id]

            total_reqs = len(reqs)
            total_cons = len(constraints)

            # Check statuses
            validated_reqs = sum(1 for r in reqs if r.status == RequirementStatus.VERIFIED)
            failed_reqs = sum(1 for r in reqs if r.status == RequirementStatus.FAILED)
            pending_reqs = sum(1 for r in reqs if r.status in (RequirementStatus.ACTIVE, RequirementStatus.DRAFT))

            violations = sum(1 for c in constraints if c.status == ConstraintStatus.VIOLATED) + failed_reqs

            if total_reqs == 0 and total_cons == 0:
                overall = ValidationStatus.PENDING
            elif violations > 0:
                overall = ValidationStatus.FAIL
            elif pending_reqs > 0:
                overall = ValidationStatus.WARNING if validated_reqs > 0 else ValidationStatus.PENDING
            else:
                overall = ValidationStatus.PASS

            return RequirementOverviewSummary(
                project_id=project_id,
                total_requirements=total_reqs,
                total_constraints=total_cons,
                validated_count=validated_reqs,
                pending_count=pending_reqs,
                violations_count=violations,
                overall_status=overall,
                last_updated=time.time(),
            )

    # ==================== DETERMINISTIC CANDIDATE EVALUATION ====================

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
                            unit=c.required_unit,
                            reason=f"Specification conflict: {conf.value_a} vs {conf.value_b}",
                        )
                    )
                    continue

                if prop_key not in spec_map:
                    constraint_results.append(
                        ConstraintResult(
                            constraint_id=c.constraint_id,
                            property=c.property,
                            required_value=f"{c.operator.value} {c.required_value}",
                            actual_value="NOT_FOUND",
                            operator=c.operator.value,
                            status=ValidationStatus.UNKNOWN,
                            unit=c.required_unit,
                            reason=f"Specification property '{c.property}' not found in candidate datasheets.",
                        )
                    )
                    has_unknown = True
                    continue

                spec = spec_map[prop_key]
                outcome = DeterministicConstraintEvaluator.evaluate(
                    constraint=c,
                    actual_val=spec.normalized_value,
                    actual_unit=spec.unit,
                )
                status = outcome.status
                reason = outcome.reason

                if status == ValidationStatus.FAIL:
                    has_fail = True
                elif status == ValidationStatus.UNKNOWN:
                    has_unknown = True

                constraint_results.append(
                    ConstraintResult(
                        constraint_id=c.constraint_id,
                        property=c.property,
                        required_value=f"{c.operator.value} {c.required_value}",
                        actual_value=spec.value,
                        operator=c.operator.value,
                        status=status,
                        unit=spec.unit or c.required_unit,
                        source_document=spec.source_document,
                        page=spec.page,
                        section=spec.section,
                        reason=reason,
                    )
                )

            # Determine overall outcome
            if has_fail:
                overall = ValidationStatus.FAIL
            elif has_conflict:
                overall = ValidationStatus.CONFLICT
            elif has_unknown:
                overall = ValidationStatus.UNKNOWN
            else:
                overall = ValidationStatus.PASS

            val_id = f"VAL-{candidate_component_id}-{int(time.time() * 1000)}"
            result = ValidationResult(
                validation_id=val_id,
                candidate_id=candidate_component_id,
                requirement_id=requirement_id,
                project_id=req.project_id,
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
