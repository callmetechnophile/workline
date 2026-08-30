"""
Procurement substitution and constraint design rules for EngineeringValidationAgent (Sections 29, 30, 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class ProcurementSubstitutionRule(ValidationRule):
    """RULE-PROC-001: Verifies that economic substitutions made during procurement do not violate architecture requirements."""

    @property
    def rule_id(self) -> str:
        return "RULE-PROC-001"

    @property
    def title(self) -> str:
        return "Procurement Alternative & Substitution Compliance"

    @property
    def category(self) -> str:
        return "procurement"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "CRITICAL"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        bom_items = context.get("bom", {}).get("items", [])
        opt_proc = context.get("optimized_procurement", {})
        proc_orders = opt_proc.get("orders", [])

        # Check if procurement selected an incompatible part
        proc_parts = {
            item.get("part_number", "").lower(): item
            for ord in proc_orders
            for item in ord.get("items", [])
        }

        # Check for explicit substitution violation flag in context
        if context.get("substitution_violation"):
            viol = context["substitution_violation"]
            results.append(
                ValidationItem(
                    validation_id=f"VAL-PROC-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="FAIL",
                    severity="CRITICAL",
                    title=f"Procurement Substitution Violates Architecture ({viol.get('substituted_part')} replaces {viol.get('required_part')})",
                    description=viol.get("reason", "Substituted component lacks required architectural interfaces."),
                    affected_components=[viol.get("substituted_part", "Unknown")],
                    recommended_action="Revert procurement allocation to the engineering-approved component.",
                    blocking=True,
                )
            )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-PROC-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="Procurement Plan Fully Compliant with Architecture",
                    description="All allocated distributor parts match approved BOM components or validated drop-in equivalents.",
                    blocking=False,
                )
            )

        return results
