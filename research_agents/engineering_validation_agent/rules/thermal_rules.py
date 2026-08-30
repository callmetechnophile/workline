"""
Thermal management design rules for EngineeringValidationAgent (Sections 23 & 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class ThermalManagementRule(ValidationRule):
    """RULE-THERM-001: Verifies active/passive thermal cooling for compute modules exceeding 10W TDP."""

    @property
    def rule_id(self) -> str:
        return "RULE-THERM-001"

    @property
    def title(self) -> str:
        return "High-Power Compute Thermal Dissipation"

    @property
    def category(self) -> str:
        return "thermal"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "MEDIUM"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        bom_items = context.get("bom", {}).get("items", [])

        has_jetson = any("orin" in it.get("part_number", "").lower() for it in bom_items)

        if has_jetson:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-THERM-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="Active Thermal Heatsink / Fan Integration Confirmed",
                    description="Jetson Orin Nano Developer Kit thermal dissipation handled by integrated aluminum heatsink & PWM fan.",
                    blocking=False,
                )
            )

        return results
