"""Engineering Requirement management service."""

from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional

from backend.workline.knowledge.models import (
    Actor,
    EngineeringDecision,
    EngineeringRequirement,
    KnowledgeAuditEvent,
    KnowledgeAuditEventType,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
)
from backend.workline.knowledge.requirements.traceability import TraceabilityChain, TraceabilityEngine, traceability_engine

logger = logging.getLogger("workline.knowledge.requirements")


class RequirementService:
    """Manages project engineering requirements, status progression, and traceability."""

    def __init__(self, engine: TraceabilityEngine = traceability_engine):
        self.engine = engine
        self._lock = threading.RLock()
        self._requirements: Dict[str, EngineeringRequirement] = {}  # req_id -> EngineeringRequirement
        self._audit_logs: List[KnowledgeAuditEvent] = []

    def create_requirement(
        self,
        req: EngineeringRequirement,
        actor: Optional[Actor] = None,
    ) -> EngineeringRequirement:
        """Creates and registers a new engineering requirement."""
        with self._lock:
            now_iso = datetime.now(timezone.utc).isoformat()
            req.created_at = now_iso
            req.updated_at = now_iso
            if actor:
                req.created_by = actor

            self._requirements[req.requirement_id] = req

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{req.requirement_id}_created",
                    event_type=KnowledgeAuditEventType.REQUIREMENT_CREATED,
                    project_id=req.project_id,
                    object_id=req.requirement_id,
                    actor=req.created_by,
                    details={"category": req.category.value, "priority": req.priority.value},
                )
            )
            return req

    def update_status(
        self,
        requirement_id: str,
        status: RequirementStatus,
        actor: Actor,
    ) -> EngineeringRequirement:
        """Updates requirement status."""
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                raise ValueError(f"Requirement '{requirement_id}' not found.")

            req.status = status
            req.updated_at = datetime.now(timezone.utc).isoformat()

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{requirement_id}_updated",
                    event_type=KnowledgeAuditEventType.REQUIREMENT_UPDATED,
                    project_id=req.project_id,
                    object_id=requirement_id,
                    actor=actor,
                    details={"new_status": status.value},
                )
            )
            return req

    def link_satisfying_decision(
        self,
        requirement_id: str,
        decision_id: str,
    ) -> EngineeringRequirement:
        """Links a decision satisfying the requirement."""
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                raise ValueError(f"Requirement '{requirement_id}' not found.")

            if decision_id not in req.satisfied_by_decisions:
                req.satisfied_by_decisions.append(decision_id)
                req.status = RequirementStatus.APPROVED

            req.updated_at = datetime.now(timezone.utc).isoformat()
            return req

    def verify_requirement(
        self,
        requirement_id: str,
        validation_id: str,
        passed: bool,
        actor: Actor,
    ) -> EngineeringRequirement:
        """Marks requirement verified (VERIFIED) or failed (FAILED)."""
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                raise ValueError(f"Requirement '{requirement_id}' not found.")

            if validation_id not in req.verified_by_validations:
                req.verified_by_validations.append(validation_id)

            req.status = RequirementStatus.VERIFIED if passed else RequirementStatus.FAILED
            req.updated_at = datetime.now(timezone.utc).isoformat()

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{requirement_id}_verified",
                    event_type=KnowledgeAuditEventType.REQUIREMENT_VERIFIED,
                    project_id=req.project_id,
                    object_id=requirement_id,
                    actor=actor,
                    details={"validation_id": validation_id, "passed": passed},
                )
            )
            return req

    def get_requirement(self, requirement_id: str) -> Optional[EngineeringRequirement]:
        """Retrieves single requirement by ID."""
        with self._lock:
            return self._requirements.get(requirement_id)

    def list_requirements(
        self,
        project_id: str,
        category: Optional[RequirementCategory] = None,
        status: Optional[RequirementStatus] = None,
    ) -> List[EngineeringRequirement]:
        """Lists requirements for a project."""
        with self._lock:
            res = [r for r in self._requirements.values() if r.project_id == project_id]
            if category:
                res = [r for r in res if r.category == category]
            if status:
                res = [r for r in res if r.status == status]
            return sorted(res, key=lambda r: r.created_at)

    def get_traceability(
        self,
        requirement_id: str,
        decisions: List[EngineeringDecision],
    ) -> TraceabilityChain:
        """Builds full traceability chain for a requirement."""
        with self._lock:
            req = self._requirements.get(requirement_id)
            if not req:
                raise ValueError(f"Requirement '{requirement_id}' not found.")
            return self.engine.build_chain(req, decisions)


requirement_service = RequirementService()
