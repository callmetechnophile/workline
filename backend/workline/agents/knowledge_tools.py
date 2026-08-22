"""Google ADK Agent Tools for Engineering Knowledge and Decision Memory."""

from typing import Any, Dict, List, Optional
from backend.workline.knowledge.models import (
    Actor,
    ActorType,
    DecisionAlternative,
    DecisionCategory,
    DecisionEvidence,
    DecisionStatus,
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
    RequirementCategory,
)
from backend.workline.knowledge.service import KnowledgeService, knowledge_service


class EngineeringKnowledgeTools:
    """Agent toolset providing contextual access to engineering knowledge, decisions, and constraints."""

    def __init__(self, svc: Optional[KnowledgeService] = None):
        self.svc = svc or knowledge_service

    def get_project_requirements(
        self,
        project_id: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch active project requirements."""
        cat_enum = RequirementCategory[category.upper()] if category and category.upper() in RequirementCategory.__members__ else None
        reqs = self.svc.list_requirements(project_id, category=cat_enum)
        return [r.model_dump() for r in reqs]

    def get_current_decisions(
        self,
        project_id: str,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch current non-superseded approved/implemented decisions."""
        cat_enum = DecisionCategory[category.upper()] if category and category.upper() in DecisionCategory.__members__ else None
        decs = self.svc.list_decisions(project_id, category=cat_enum)
        # Filter to active authority
        active = [d for d in decs if d.status in (DecisionStatus.APPROVED, DecisionStatus.IMPLEMENTED, DecisionStatus.VALIDATED)]
        return [d.model_dump() for d in active]

    def search_engineering_knowledge(
        self,
        project_id: str,
        query: str,
        object_types: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic hybrid search across decisions, requirements, findings, and lessons."""
        results = self.svc.search_knowledge(project_id, query, object_types=object_types)
        return [r.model_dump() for r in results]

    def get_decision_evidence(self, decision_id: str) -> List[Dict[str, Any]]:
        """Retrieve evidence backing a decision."""
        dec = self.svc.get_decision(decision_id)
        if not dec:
            return []
        return [e.model_dump() for e in dec.evidence]

    def get_component_decision_history(
        self,
        project_id: str,
        component_name: str,
    ) -> List[Dict[str, Any]]:
        """Retrieve historical decisions regarding a component."""
        decs = self.svc.list_decisions(project_id, category=DecisionCategory.COMPONENT_SELECTION)
        matching = [
            d for d in decs
            if component_name.lower() in d.selected_option.lower() or any(component_name.lower() in a.name.lower() for a in d.alternatives)
        ]
        return [d.model_dump() for d in matching]

    def get_validation_history(self, project_id: str) -> List[Dict[str, Any]]:
        """Retrieve validation records and outcomes."""
        decs = self.svc.list_decisions(project_id)
        validated = [d for d in decs if d.validation_status is not None]
        return [
            {
                "decision_id": d.decision_id,
                "title": d.title,
                "selected_option": d.selected_option,
                "validation_status": d.validation_status,
                "validation_id": d.metadata.get("validation_id"),
            }
            for d in validated
        ]

    def get_engineering_lessons(self, project_id: str) -> List[Dict[str, Any]]:
        """Retrieve lessons learned and recommendations."""
        lessons = self.svc.list_lessons(project_id)
        return [l.model_dump() for l in lessons]

    def detect_requirement_conflicts(self, project_id: str) -> Dict[str, Any]:
        """Runs automated conflict scan across requirements and active decisions."""
        report = self.svc.detect_conflicts(project_id)
        return report.model_dump()

    def create_decision_proposal(
        self,
        project_id: str,
        title: str,
        category: str,
        problem: str,
        rationale: str,
        selected_option: str,
        agent_id: str,
        constraints: Optional[List[str]] = None,
        alternatives: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Proposes an engineering decision. Created in PROPOSED status for human review."""
        cat_enum = DecisionCategory[category.upper()] if category.upper() in DecisionCategory.__members__ else DecisionCategory.SYSTEM_ARCHITECTURE
        import secrets
        dec_id = f"dec_{secrets.token_hex(4)}"

        alts = [
            DecisionAlternative(
                alternative_id=f"alt_{secrets.token_hex(3)}",
                decision_id=dec_id,
                name=a.get("name", "Option"),
                description=a.get("description", ""),
                advantages=a.get("advantages", []),
                disadvantages=a.get("disadvantages", []),
                rejection_reason=a.get("rejection_reason"),
            )
            for a in (alternatives or [])
        ]

        dec = EngineeringDecision(
            decision_id=dec_id,
            project_id=project_id,
            title=title,
            description=rationale,
            category=cat_enum,
            status=DecisionStatus.PROPOSED,
            created_by=Actor(actor_type=ActorType.AGENT, actor_id=agent_id),
            problem=problem,
            rationale=rationale,
            selected_option=selected_option,
            constraints=constraints or [],
            alternatives=alts,
        )
        created = self.svc.create_decision(dec, actor=Actor(actor_type=ActorType.AGENT, actor_id=agent_id))
        return created.model_dump()

    def approve_decision(
        self,
        decision_id: str,
        actor_id: str,
        actor_type: str = "HUMAN",
    ) -> Dict[str, Any]:
        """Approves a decision. Requires HUMAN actor authorization."""
        act_type = ActorType[actor_type.upper()] if actor_type.upper() in ActorType.__members__ else ActorType.HUMAN
        actor = Actor(actor_type=act_type, actor_id=actor_id)
        approved = self.svc.approve_decision(decision_id, actor=actor)
        return approved.model_dump()

    def reject_decision(
        self,
        decision_id: str,
        actor_id: str,
        actor_type: str = "HUMAN",
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Rejects a decision."""
        act_type = ActorType[actor_type.upper()] if actor_type.upper() in ActorType.__members__ else ActorType.HUMAN
        actor = Actor(actor_type=act_type, actor_id=actor_id)
        rejected = self.svc.reject_decision(decision_id, actor=actor, reason=reason)
        return rejected.model_dump()


# Singleton
knowledge_tools = EngineeringKnowledgeTools()
