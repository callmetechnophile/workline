"""
Abstract base class for modular deterministic design rule checks (Section 34).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class ValidationRule(ABC):
    """Abstract interface for a modular engineering design verification rule."""

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """Unique identifier (e.g. 'RULE-ELEC-001')."""
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        """Short descriptive title."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Rule category (e.g. electrical, power, interface, bom, procurement)."""
        pass

    @property
    @abstractmethod
    def default_severity(self) -> ValidationSeverityLiteral:
        """Default severity level when this rule fails."""
        pass

    @abstractmethod
    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        """
        Evaluates the engineering design context against this rule.

        Returns:
            List of ValidationItem results (PASS, FAIL, WARNING, UNKNOWN).
        """
        pass
