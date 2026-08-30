"""
BOM completeness and procurement plan verification service for EngineeringValidationAgent (Sections 26, 27, 28, 29, 30).
"""

from typing import Any, Dict, List
from research_agents.engineering_validation_agent.rules.bom_rules import (
    MissingComponentRule,
    QuantityConsistencyRule,
    SupportingPassivesRule,
)
from research_agents.engineering_validation_agent.rules.procurement_rules import ProcurementSubstitutionRule
from research_agents.engineering_validation_agent.schemas import ValidationItem


class BOMProcurementValidator:
    """Verifies BOM completeness, quantities, supporting components, and procurement substitution compliance."""

    def __init__(
        self,
        missing_rule: MissingComponentRule = None,
        qty_rule: QuantityConsistencyRule = None,
        passive_rule: SupportingPassivesRule = None,
        subst_rule: ProcurementSubstitutionRule = None,
    ):
        self.missing_rule = missing_rule or MissingComponentRule()
        self.qty_rule = qty_rule or QuantityConsistencyRule()
        self.passive_rule = passive_rule or SupportingPassivesRule()
        self.subst_rule = subst_rule or ProcurementSubstitutionRule()

    def validate_bom(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        results.extend(self.missing_rule.check(context))
        results.extend(self.qty_rule.check(context))
        results.extend(self.passive_rule.check(context))
        return results

    def validate_procurement(self, context: Dict[str, Any]) -> List[ValidationItem]:
        return self.subst_rule.check(context)
