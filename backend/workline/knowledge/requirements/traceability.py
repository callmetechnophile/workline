"""End-to-end engineering requirement traceability graph builder."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from backend.workline.knowledge.models import (
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
)


class TraceabilityStep(BaseModel):
    """Single stage in the requirement execution lifecycle."""
    stage: str  # REQUIREMENT, DECISION, IMPLEMENTATION, VALIDATION, FINDING, LESSON
    identifier: str
    title: str
    status: str
    details: Dict[str, Any] = Field(default_factory=dict)


class TraceabilityChain(BaseModel):
    """Complete traceable path from requirement to validation and lessons learned."""
    requirement_id: str
    project_id: str
    title: str
    category: str
    status: str
    steps: List[TraceabilityStep] = Field(default_factory=list)
    decisions: List[Dict[str, Any]] = Field(default_factory=list)
    implementations: List[Dict[str, Any]] = Field(default_factory=list)
    validations: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    lessons: List[Dict[str, Any]] = Field(default_factory=list)


class TraceabilityEngine:
    """Constructs multi-hop traceability graphs across requirements, decisions, and validations."""

    def build_chain(
        self,
        requirement: EngineeringRequirement,
        decisions: List[EngineeringDecision],
        findings: Optional[List[EngineeringFinding]] = None,
        lessons: Optional[List[EngineeringLesson]] = None,
    ) -> TraceabilityChain:
        """Assembles a full traceability chain for a requirement."""
        chain = TraceabilityChain(
            requirement_id=requirement.requirement_id,
            project_id=requirement.project_id,
            title=requirement.title,
            category=requirement.category.value,
            status=requirement.status.value,
        )

        # 1. Requirement Step
        chain.steps.append(
            TraceabilityStep(
                stage="REQUIREMENT",
                identifier=requirement.requirement_id,
                title=requirement.title,
                status=requirement.status.value,
                details={"value": requirement.value, "unit": requirement.unit},
            )
        )

        # 2. Linked Decisions
        matching_decisions = [
            d for d in decisions
            if d.decision_id in requirement.satisfied_by_decisions or requirement.requirement_id in str(d.metadata)
        ]

        for d in matching_decisions:
            chain.decisions.append({
                "decision_id": d.decision_id,
                "title": d.title,
                "selected_option": d.selected_option,
                "status": d.status.value,
            })
            chain.steps.append(
                TraceabilityStep(
                    stage="DECISION",
                    identifier=d.decision_id,
                    title=f"{d.title} ({d.selected_option})",
                    status=d.status.value,
                    details={"rationale": d.rationale},
                )
            )

            # 3. Implementations
            for imp in d.implemented_objects:
                chain.implementations.append({"object_id": imp, "decision_id": d.decision_id})
                chain.steps.append(
                    TraceabilityStep(
                        stage="IMPLEMENTATION",
                        identifier=imp,
                        title=f"Implementation: {imp}",
                        status="IMPLEMENTED",
                        details={"decision_id": d.decision_id},
                    )
                )

            # 4. Validations
            if d.validation_status:
                chain.validations.append({
                    "decision_id": d.decision_id,
                    "validation_status": d.validation_status,
                })
                chain.steps.append(
                    TraceabilityStep(
                        stage="VALIDATION",
                        identifier=f"val_{d.decision_id}",
                        title=f"Validation: {d.validation_status}",
                        status=d.validation_status,
                        details={"decision_id": d.decision_id},
                    )
                )

        return chain


traceability_engine = TraceabilityEngine()
