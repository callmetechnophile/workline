"""Validation rules for engineering decisions."""

from typing import List, Optional
from backend.workline.knowledge.models import DecisionAlternative, DecisionEvidence, EngineeringDecision


class DecisionValidationError(Exception):
    """Raised when decision parameters fail validation."""
    pass


class DecisionValidator:
    """Validates structural completeness and logical integrity of decisions."""

    @classmethod
    def validate_decision(cls, decision: EngineeringDecision) -> None:
        """Validates that a decision contains mandatory problem, selection, and options."""
        if not decision.title.strip():
            raise DecisionValidationError("Decision title cannot be empty.")

        if not decision.selected_option.strip():
            raise DecisionValidationError("Decision must specify a selected_option.")

        if not decision.project_id.strip():
            raise DecisionValidationError("Decision must be associated with a valid project_id.")
