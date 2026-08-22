"""Engineering Decision management service."""

from datetime import datetime, timezone
import logging
import threading
from typing import Any, Dict, List, Optional, Tuple

from backend.workline.knowledge.decisions.validator import DecisionValidator
from backend.workline.knowledge.models import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionStatus,
    EngineeringDecision,
    KnowledgeAuditEvent,
    KnowledgeAuditEventType,
)

logger = logging.getLogger("workline.knowledge.decisions")


class UnauthorizedApprovalError(Exception):
    """Raised when an unauthorized actor (e.g. unapproved agent) attempts to approve a decision."""
    pass


class DecisionService:
    """
    Authoritative lifecycle service for engineering decisions, alternatives,
    evidence, implementation linking, validation linking, and supersession.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._decisions: Dict[str, EngineeringDecision] = {}  # decision_id -> EngineeringDecision
        self._audit_logs: List[KnowledgeAuditEvent] = []

    def create_decision(
        self,
        decision: EngineeringDecision,
        actor: Optional[Actor] = None,
    ) -> EngineeringDecision:
        """
        Creates a new engineering decision.
        If created by an AI agent, status is strictly set to PROPOSED.
        """
        DecisionValidator.validate_decision(decision)
        current_actor = actor or decision.created_by

        with self._lock:
            # AI agent proposals cannot self-approve without human authorization
            if current_actor.actor_type == ActorType.AGENT and decision.status == DecisionStatus.APPROVED:
                decision.status = DecisionStatus.PROPOSED

            now_iso = datetime.now(timezone.utc).isoformat()
            decision.created_at = now_iso
            decision.updated_at = now_iso
            decision.created_by = current_actor

            self._decisions[decision.decision_id] = decision

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{decision.decision_id}_created",
                    event_type=KnowledgeAuditEventType.DECISION_CREATED,
                    project_id=decision.project_id,
                    object_id=decision.decision_id,
                    actor=current_actor,
                    details={"status": decision.status.value, "selected_option": decision.selected_option},
                )
            )
            return decision

    def approve_decision(
        self,
        decision_id: str,
        actor: Actor,
    ) -> EngineeringDecision:
        """
        Approves a proposed engineering decision.
        Requires HUMAN or authorized system role.
        """
        if actor.actor_type == ActorType.AGENT:
            raise UnauthorizedApprovalError("Agents cannot unilaterally approve engineering decisions without human approval.")

        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                raise ValueError(f"Decision '{decision_id}' not found.")

            decision.status = DecisionStatus.APPROVED
            decision.updated_at = datetime.now(timezone.utc).isoformat()

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{decision_id}_approved",
                    event_type=KnowledgeAuditEventType.DECISION_APPROVED,
                    project_id=decision.project_id,
                    object_id=decision_id,
                    actor=actor,
                    details={"status": DecisionStatus.APPROVED.value},
                )
            )
            return decision

    def reject_decision(
        self,
        decision_id: str,
        actor: Actor,
        reason: Optional[str] = None,
    ) -> EngineeringDecision:
        """Rejects a proposed decision."""
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                raise ValueError(f"Decision '{decision_id}' not found.")

            decision.status = DecisionStatus.REJECTED
            decision.updated_at = datetime.now(timezone.utc).isoformat()
            if reason:
                decision.metadata["rejection_reason"] = reason

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{decision_id}_rejected",
                    event_type=KnowledgeAuditEventType.DECISION_REJECTED,
                    project_id=decision.project_id,
                    object_id=decision_id,
                    actor=actor,
                    details={"reason": reason},
                )
            )
            return decision

    def supersede_decision(
        self,
        old_decision_id: str,
        new_decision: EngineeringDecision,
        actor: Actor,
    ) -> Tuple[EngineeringDecision, EngineeringDecision]:
        """
        Supersedes an existing decision with a new decision.
        Preserves historical decision record and establishes bidirectional links.
        """
        with self._lock:
            old_dec = self._decisions.get(old_decision_id)
            if not old_dec:
                raise ValueError(f"Old decision '{old_decision_id}' not found.")

            # Create new decision first
            new_decision.supersedes = old_decision_id
            created_new = self.create_decision(new_decision, actor=actor)

            # Update old decision status to SUPERSEDED and link pointer
            now_iso = datetime.now(timezone.utc).isoformat()
            old_dec.status = DecisionStatus.SUPERSEDED
            old_dec.superseded_by = created_new.decision_id
            old_dec.updated_at = now_iso

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{old_decision_id}_superseded",
                    event_type=KnowledgeAuditEventType.DECISION_SUPERSEDED,
                    project_id=old_dec.project_id,
                    object_id=old_decision_id,
                    actor=actor,
                    details={"superseded_by": created_new.decision_id},
                )
            )
            return old_dec, created_new

    def link_implementation(
        self,
        decision_id: str,
        engineering_object_id: str,
    ) -> EngineeringDecision:
        """Links an engineering object (e.g. Component, PCB net, firmware module) to a decision."""
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                raise ValueError(f"Decision '{decision_id}' not found.")

            if engineering_object_id not in decision.implemented_objects:
                decision.implemented_objects.append(engineering_object_id)
            
            decision.status = DecisionStatus.IMPLEMENTED
            decision.updated_at = datetime.now(timezone.utc).isoformat()
            return decision

    def link_validation(
        self,
        decision_id: str,
        validation_status: str,
        validation_id: Optional[str] = None,
    ) -> EngineeringDecision:
        """Links a validation run outcome (PASS/FAIL) to the decision."""
        with self._lock:
            decision = self._decisions.get(decision_id)
            if not decision:
                raise ValueError(f"Decision '{decision_id}' not found.")

            decision.validation_status = validation_status
            decision.updated_at = datetime.now(timezone.utc).isoformat()
            if validation_id:
                decision.metadata["validation_id"] = validation_id

            if validation_status.upper() == "PASS":
                decision.status = DecisionStatus.VALIDATED

            return decision

    def get_decision(self, decision_id: str) -> Optional[EngineeringDecision]:
        """Retrieves a single decision by ID."""
        with self._lock:
            return self._decisions.get(decision_id)

    def list_decisions(
        self,
        project_id: str,
        category: Optional[DecisionCategory] = None,
        status: Optional[DecisionStatus] = None,
    ) -> List[EngineeringDecision]:
        """Lists decisions for a given project with optional category and status filtering."""
        with self._lock:
            res = [d for d in self._decisions.values() if d.project_id == project_id]
            if category:
                res = [d for d in res if d.category == category]
            if status:
                res = [d for d in res if d.status == status]
            return sorted(res, key=lambda d: d.created_at)


decision_service = DecisionService()
