"""Unified KnowledgeService coordinating decisions, requirements, findings, lessons, retrieval, and conflicts."""

from typing import Any, Dict, List, Optional, Tuple

from backend.workline.knowledge.conflicts import ConflictDetector, ConflictReport, conflict_detector
from backend.workline.knowledge.decisions.service import DecisionService, decision_service
from backend.workline.knowledge.findings.service import FindingService, finding_service
from backend.workline.knowledge.indexing import KnowledgeIndexer, knowledge_indexer
from backend.workline.knowledge.lessons.service import LessonService, lesson_service
from backend.workline.knowledge.models import (
    Actor,
    DecisionCategory,
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
    KnowledgeAuditEvent,
    RequirementCategory,
    RequirementStatus,
)
from backend.workline.knowledge.requirements.service import RequirementService, requirement_service
from backend.workline.knowledge.requirements.traceability import TraceabilityChain
from backend.workline.knowledge.retrieval import KnowledgeRetrievalService, RetrievedKnowledgeItem, knowledge_retrieval


class KnowledgeService:
    """
    Central orchestration service for Engineering Knowledge and Decision Memory.
    Coordinates structured state, Qdrant vector indexing, hybrid retrieval,
    conflict detection, and requirement-to-validation traceability.
    """

    def __init__(
        self,
        decisions: DecisionService = decision_service,
        requirements: RequirementService = requirement_service,
        findings: FindingService = finding_service,
        lessons: LessonService = lesson_service,
        indexer: KnowledgeIndexer = knowledge_indexer,
        retrieval: KnowledgeRetrievalService = knowledge_retrieval,
        conflicts: ConflictDetector = conflict_detector,
    ):
        self.decisions = decisions
        self.requirements = requirements
        self.findings = findings
        self.lessons = lessons
        self.indexer = indexer
        self.retrieval = retrieval
        self.conflicts = conflicts

    # ---------------------------------------------------------
    # Decision Operations
    # ---------------------------------------------------------

    def create_decision(
        self,
        decision: EngineeringDecision,
        actor: Optional[Actor] = None,
    ) -> EngineeringDecision:
        """Creates decision and indexes semantic payload in Qdrant."""
        dec = self.decisions.create_decision(decision, actor=actor)
        self.indexer.index_decision(dec)
        return dec

    def approve_decision(
        self,
        decision_id: str,
        actor: Actor,
    ) -> EngineeringDecision:
        """Approves proposed decision and updates index."""
        dec = self.decisions.approve_decision(decision_id, actor=actor)
        self.indexer.index_decision(dec)
        return dec

    def reject_decision(
        self,
        decision_id: str,
        actor: Actor,
        reason: Optional[str] = None,
    ) -> EngineeringDecision:
        """Rejects decision and updates index."""
        dec = self.decisions.reject_decision(decision_id, actor=actor, reason=reason)
        self.indexer.index_decision(dec)
        return dec

    def supersede_decision(
        self,
        old_decision_id: str,
        new_decision: EngineeringDecision,
        actor: Actor,
    ) -> Tuple[EngineeringDecision, EngineeringDecision]:
        """Supersedes previous decision with new decision and updates index for both."""
        old_dec, new_dec = self.decisions.supersede_decision(old_decision_id, new_decision, actor=actor)
        self.indexer.index_decision(old_dec)
        self.indexer.index_decision(new_dec)
        return old_dec, new_dec

    def get_decision(self, decision_id: str) -> Optional[EngineeringDecision]:
        return self.decisions.get_decision(decision_id)

    def list_decisions(
        self,
        project_id: str,
        category: Optional[DecisionCategory] = None,
        status: Optional[DecisionStatus] = None,
    ) -> List[EngineeringDecision]:
        return self.decisions.list_decisions(project_id, category=category, status=status)

    # ---------------------------------------------------------
    # Requirement Operations
    # ---------------------------------------------------------

    def create_requirement(
        self,
        req: EngineeringRequirement,
        actor: Optional[Actor] = None,
    ) -> EngineeringRequirement:
        """Creates requirement and indexes in Qdrant."""
        created = self.requirements.create_requirement(req, actor=actor)
        self.indexer.index_requirement(created)
        return created

    def verify_requirement(
        self,
        requirement_id: str,
        validation_id: str,
        passed: bool,
        actor: Actor,
    ) -> EngineeringRequirement:
        """Verifies requirement status."""
        req = self.requirements.verify_requirement(requirement_id, validation_id, passed, actor)
        self.indexer.index_requirement(req)
        return req

    def get_requirement(self, requirement_id: str) -> Optional[EngineeringRequirement]:
        return self.requirements.get_requirement(requirement_id)

    def list_requirements(
        self,
        project_id: str,
        category: Optional[RequirementCategory] = None,
        status: Optional[RequirementStatus] = None,
    ) -> List[EngineeringRequirement]:
        return self.requirements.list_requirements(project_id, category=category, status=status)

    def get_requirement_traceability(self, requirement_id: str) -> TraceabilityChain:
        """Returns multi-hop traceability graph for a requirement."""
        req = self.requirements.get_requirement(requirement_id)
        if not req:
            raise ValueError(f"Requirement '{requirement_id}' not found.")
        all_decisions = self.decisions.list_decisions(req.project_id)
        all_findings = self.findings.list_findings(req.project_id)
        all_lessons = self.lessons.list_lessons(req.project_id)
        return self.requirements.get_traceability(requirement_id, all_decisions)

    # ---------------------------------------------------------
    # Finding Operations
    # ---------------------------------------------------------

    def create_finding(
        self,
        finding: EngineeringFinding,
        actor: Optional[Actor] = None,
    ) -> EngineeringFinding:
        created = self.findings.create_finding(finding, actor=actor)
        self.indexer.index_finding(created)
        return created

    def resolve_finding(
        self,
        finding_id: str,
        resolution: str,
        resolved_by_decision_id: Optional[str] = None,
        actor: Optional[Actor] = None,
    ) -> EngineeringFinding:
        resolved = self.findings.resolve_finding(finding_id, resolution, resolved_by_decision_id, actor=actor)
        self.indexer.index_finding(resolved)
        return resolved

    def get_finding(self, finding_id: str) -> Optional[EngineeringFinding]:
        return self.findings.get_finding(finding_id)

    def list_findings(self, project_id: str) -> List[EngineeringFinding]:
        return self.findings.list_findings(project_id)

    # ---------------------------------------------------------
    # Lesson Operations
    # ---------------------------------------------------------

    def create_lesson(
        self,
        lesson: EngineeringLesson,
        actor: Optional[Actor] = None,
    ) -> EngineeringLesson:
        created = self.lessons.create_lesson(lesson, actor=actor)
        self.indexer.index_lesson(created)
        return created

    def get_lesson(self, lesson_id: str) -> Optional[EngineeringLesson]:
        return self.lessons.get_lesson(lesson_id)

    def list_lessons(self, project_id: str) -> List[EngineeringLesson]:
        return self.lessons.list_lessons(project_id)

    # ---------------------------------------------------------
    # Hybrid Retrieval & Conflict Detection
    # ---------------------------------------------------------

    def search_knowledge(
        self,
        project_id: str,
        query: str,
        object_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[RetrievedKnowledgeItem]:
        """Executes hybrid search with live SurrealDB state validation."""
        authoritative: Dict[str, Any] = {}
        for d in self.decisions.list_decisions(project_id):
            authoritative[d.decision_id] = d
        for r in self.requirements.list_requirements(project_id):
            authoritative[r.requirement_id] = r
        for f in self.findings.list_findings(project_id):
            authoritative[f.finding_id] = f
        for l in self.lessons.list_lessons(project_id):
            authoritative[l.lesson_id] = l

        return self.retrieval.search_project_knowledge(
            project_id=project_id,
            query=query,
            object_types=object_types,
            authoritative_store=authoritative,
            limit=limit,
        )

    def detect_conflicts(self, project_id: str) -> ConflictReport:
        """Scans project knowledge for constraint and requirement conflicts."""
        reqs = self.requirements.list_requirements(project_id)
        decs = self.decisions.list_decisions(project_id)
        return self.conflicts.detect_conflicts(project_id, reqs, decs)

    def get_audit_trail(self, project_id: Optional[str] = None) -> List[KnowledgeAuditEvent]:
        """Collects audit trail events across all knowledge subsystems."""
        all_events = (
            self.decisions._audit_logs
            + self.requirements._audit_logs
            + self.findings._audit_logs
            + self.lessons._audit_logs
        )
        if project_id:
            all_events = [e for e in all_events if e.project_id == project_id]
        return sorted(all_events, key=lambda e: e.timestamp)


# Module singleton
knowledge_service = KnowledgeService()
