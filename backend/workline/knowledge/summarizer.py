"""Engineering Knowledge summarizer and report formatter."""

from typing import List, Optional
from backend.workline.knowledge.models import (
    EngineeringDecision,
    EngineeringFinding,
    EngineeringLesson,
    EngineeringRequirement,
)
from backend.workline.knowledge.requirements.traceability import TraceabilityChain


class KnowledgeSummarizer:
    """Formats engineering memory into structured human-readable and agent-readable summaries."""

    @classmethod
    def format_decision_summary(cls, decision: EngineeringDecision) -> str:
        """Formats decision details, evidence, and rationale."""
        lines = [
            f"Decision: {decision.title} [{decision.decision_id}]",
            f"Status: {decision.status.value}",
            f"Category: {decision.category.value}",
            f"Selected: {decision.selected_option}",
            f"Problem: {decision.problem}",
            f"Rationale: {decision.rationale}",
        ]
        if decision.constraints:
            lines.append(f"Constraints: {', '.join(decision.constraints)}")
        if decision.alternatives:
            lines.append("Alternatives Evaluated:")
            for alt in decision.alternatives:
                lines.append(f"  - {alt.name}: {alt.description} (Rejection reason: {alt.rejection_reason or 'None'})")
        if decision.evidence:
            lines.append("Evidence:")
            for ev in decision.evidence:
                lines.append(f"  - [{ev.source_type.value}] {ev.title}: {ev.claim}")
        if decision.supersedes:
            lines.append(f"Supersedes: {decision.supersedes}")
        if decision.superseded_by:
            lines.append(f"Superseded By: {decision.superseded_by}")
        if decision.project_version:
            lines.append(f"Project Version: {decision.project_version}")
        if decision.git_commit:
            lines.append(f"Git Commit: {decision.git_commit}")
        return "\n".join(lines)

    @classmethod
    def format_traceability_summary(cls, chain: TraceabilityChain) -> str:
        """Formats requirement traceability path."""
        lines = [
            f"REQUIREMENT: {chain.requirement_id} - '{chain.title}' [{chain.status}]",
        ]
        for step in chain.steps[1:]:
            lines.append(f"    ↓\n{step.stage}: {step.title} [{step.status}]")
        return "\n".join(lines)


knowledge_summarizer = KnowledgeSummarizer()
