"""
Deterministic ValidationEngine executing modular design rule checks (Sections 34, 35, 37, 38).
"""

from typing import Any, Dict, List, Tuple
from loguru import logger
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.rules.bom_rules import (
    MissingComponentRule,
    QuantityConsistencyRule,
    SupportingPassivesRule,
)
from research_agents.engineering_validation_agent.rules.electrical_rules import LogicVoltageMismatchRule
from research_agents.engineering_validation_agent.rules.interface_rules import (
    I2CAddressCollisionRule,
    InterfaceProtocolMatchRule,
)
from research_agents.engineering_validation_agent.rules.mechanical_rules import MechanicalMountingRule
from research_agents.engineering_validation_agent.rules.power_rules import (
    BatteryCapacityRule,
    PowerLoadCapacityRule,
)
from research_agents.engineering_validation_agent.rules.procurement_rules import ProcurementSubstitutionRule
from research_agents.engineering_validation_agent.rules.resource_rules import PeripheralResourceExhaustionRule
from research_agents.engineering_validation_agent.rules.software_rules import SoftwareToolchainCompatibilityRule
from research_agents.engineering_validation_agent.rules.thermal_rules import ThermalManagementRule
from research_agents.engineering_validation_agent.schemas import (
    FinalVerdict,
    ValidationItem,
    VerdictLiteral,
)


class ValidationEngine:
    """Executes deterministic engineering design rules and computes the final quality gate verdict."""

    def __init__(self, rules: List[ValidationRule] = None):
        self.rules: List[ValidationRule] = rules or [
            LogicVoltageMismatchRule(),
            PowerLoadCapacityRule(),
            BatteryCapacityRule(),
            InterfaceProtocolMatchRule(),
            I2CAddressCollisionRule(),
            PeripheralResourceExhaustionRule(),
            MissingComponentRule(),
            QuantityConsistencyRule(),
            SupportingPassivesRule(),
            ProcurementSubstitutionRule(),
            SoftwareToolchainCompatibilityRule(),
            ThermalManagementRule(),
            MechanicalMountingRule(),
        ]

    def register_rule(self, rule: ValidationRule) -> None:
        self.rules.append(rule)

    def execute_rules(self, context: Dict[str, Any]) -> Tuple[List[ValidationItem], FinalVerdict]:
        """
        Executes all active rules across design context.

        Returns:
            Tuple of (all_findings, final_verdict)
        """
        all_findings: List[ValidationItem] = []

        for rule in self.rules:
            try:
                findings = rule.check(context)
                all_findings.extend(findings)
            except Exception as e:
                logger.error(f"[ValidationEngine] Error executing rule '{rule.rule_id}': {e}")

        # Compute Verdict (Section 37 & 38)
        crit_fails = [f for f in all_findings if f.status == "FAIL" and f.severity == "CRITICAL"]
        high_fails = [f for f in all_findings if f.status == "FAIL" and f.severity == "HIGH"]
        med_fails = [f for f in all_findings if f.status == "FAIL" and f.severity == "MEDIUM"]
        warnings = [f for f in all_findings if f.status == "WARNING"]
        unknowns = [f for f in all_findings if f.status == "UNKNOWN"]

        verdict: VerdictLiteral = "READY"
        recommendation = "Design satisfies all engineering rules and is ready for execution."

        if crit_fails or any(f.blocking for f in high_fails):
            verdict = "BLOCKED"
            reasons = [f.title for f in (crit_fails + high_fails)[:2]]
            recommendation = f"Design is BLOCKED due to critical technical violations: {'; '.join(reasons)}."
        elif high_fails or med_fails:
            verdict = "BLOCKED"
            recommendation = "Design is BLOCKED due to unresolved engineering failures."
        elif unknowns and any(u.severity in ("HIGH", "CRITICAL") for u in unknowns):
            verdict = "INCOMPLETE"
            recommendation = "Design is INCOMPLETE due to missing critical specifications."
        elif warnings or unknowns:
            verdict = "READY_WITH_WARNINGS"
            recommendation = "Design is approved with non-blocking warnings and pending validation items."

        final_verdict = FinalVerdict(
            verdict=verdict,
            critical_failures=len(crit_fails),
            high_failures=len(high_fails),
            medium_failures=len(med_fails),
            warnings=len(warnings),
            unknowns=len(unknowns),
            requirements_passed=context.get("req_passed", 0),
            requirements_failed=context.get("req_failed", 0),
            requirements_unknown=context.get("req_unknown", 0),
            recommendation=recommendation,
        )

        return all_findings, final_verdict
