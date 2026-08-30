"""
Power budget and battery capacity verification service for EngineeringValidationAgent (Sections 15, 16, 17).
"""

from typing import Any, Dict, List
from research_agents.engineering_validation_agent.rules.power_rules import BatteryCapacityRule, PowerLoadCapacityRule
from research_agents.engineering_validation_agent.schemas import ValidationItem


class PowerValidator:
    """Evaluates DC power domain headroom, regulator currents, and battery capacity."""

    def __init__(
        self,
        load_rule: PowerLoadCapacityRule = None,
        bat_rule: BatteryCapacityRule = None,
    ):
        self.load_rule = load_rule or PowerLoadCapacityRule()
        self.bat_rule = bat_rule or BatteryCapacityRule()

    def validate_power(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        results.extend(self.load_rule.check(context))
        results.extend(self.bat_rule.check(context))
        return results
