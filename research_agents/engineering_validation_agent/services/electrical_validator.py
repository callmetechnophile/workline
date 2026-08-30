"""
Electrical and logic level verification service for EngineeringValidationAgent (Section 14).
"""

from typing import Any, Dict, List
from research_agents.engineering_validation_agent.rules.electrical_rules import LogicVoltageMismatchRule
from research_agents.engineering_validation_agent.schemas import ValidationItem


class ElectricalValidator:
    """Evaluates electrical voltage rails, logic levels, and signal integrity."""

    def __init__(self, rule: LogicVoltageMismatchRule = None):
        self.voltage_rule = rule or LogicVoltageMismatchRule()

    def validate_electrical(self, context: Dict[str, Any]) -> List[ValidationItem]:
        return self.voltage_rule.check(context)
