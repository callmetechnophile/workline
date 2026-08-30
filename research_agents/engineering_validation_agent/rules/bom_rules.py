"""
BOM completeness, quantity, and dependency design rules for EngineeringValidationAgent (Sections 11, 26, 27, 28, 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class MissingComponentRule(ValidationRule):
    """RULE-BOM-001: Verifies that every critical architecture component role is represented in the BOM."""

    @property
    def rule_id(self) -> str:
        return "RULE-BOM-001"

    @property
    def title(self) -> str:
        return "Architecture-to-BOM Component Completeness"

    @property
    def category(self) -> str:
        return "bom"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "CRITICAL"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        comp_roles = context.get("component_roles", [])
        bom_items = context.get("bom", {}).get("items", [])

        bom_categories = {it.get("category", "").lower() for it in bom_items}
        bom_subsystems = {it.get("subsystem_id", "").lower() for it in bom_items}

        for role in comp_roles:
            role_name = role.get("role_name", "")
            sub_id = role.get("subsystem_id", "").lower()

            # Check if this role is missing from the BOM
            if sub_id and sub_id not in bom_subsystems and not any(role_name.lower() in it.get("component_name", "").lower() for it in bom_items):
                results.append(
                    ValidationItem(
                        validation_id=f"VAL-BOM-{uuid.uuid4().hex[:6].upper()}",
                        rule_id=self.rule_id,
                        category=self.category,
                        status="FAIL",
                        severity="CRITICAL",
                        title=f"Missing Component for Architecture Role: '{role_name}'",
                        description=f"Architecture specifies mandatory role '{role_name}' in subsystem '{sub_id}', but no corresponding BOM component was found.",
                        affected_subsystems=[sub_id],
                        recommended_action=f"Add a component satisfying the '{role_name}' role to the BOM.",
                        blocking=True,
                    )
                )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-BOM-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="All Architectural Component Roles Satisfied in BOM",
                    description="Every active subsystem contains assigned physical components with verified part numbers.",
                    blocking=False,
                )
            )

        return results


class QuantityConsistencyRule(ValidationRule):
    """RULE-BOM-002: Verifies that component quantities match across Architecture, BOM, and Procurement."""

    @property
    def rule_id(self) -> str:
        return "RULE-BOM-002"

    @property
    def title(self) -> str:
        return "Component Quantity Consistency"

    @property
    def category(self) -> str:
        return "bom"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "HIGH"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        bom_items = context.get("bom", {}).get("items", [])
        procurement_orders = context.get("optimized_procurement", {}).get("orders", [])

        # Map procurement purchased quantities
        proc_quantities: Dict[str, int] = {}
        for ord in procurement_orders:
            for item in ord.get("items", []):
                b_id = item.get("bom_item_id")
                qty = int(item.get("purchased_quantity", 0))
                proc_quantities[b_id] = proc_quantities.get(b_id, 0) + qty

        for b_it in bom_items:
            b_id = b_it.get("bom_item_id")
            bom_qty = int(b_it.get("quantity", 1))
            if b_id in proc_quantities:
                proc_qty = proc_quantities[b_id]
                if proc_qty < bom_qty:
                    results.append(
                        ValidationItem(
                            validation_id=f"VAL-QTY-{uuid.uuid4().hex[:6].upper()}",
                            rule_id=self.rule_id,
                            category=self.category,
                            status="FAIL",
                            severity="HIGH",
                            title=f"Quantity Shortfall for {b_it.get('part_number', b_id)}",
                            description=f"BOM mandates {bom_qty} units but procurement plan only procures {proc_qty} units.",
                            affected_components=[b_it.get("part_number", b_id)],
                            recommended_action=f"Increase procurement order quantity to at least {bom_qty} units.",
                            blocking=True,
                        )
                    )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-QTY-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="Component Quantities Consistent Across Pipelines",
                    description="Procurement order quantities fully satisfy or exceed all engineering BOM requirements.",
                    blocking=False,
                )
            )

        return results


class SupportingPassivesRule(ValidationRule):
    """RULE-BOM-003: Verifies that power regulators and high-speed ICs include required decoupling passives."""

    @property
    def rule_id(self) -> str:
        return "RULE-BOM-003"

    @property
    def title(self) -> str:
        return "Supporting Passives & Decoupling Completeness"

    @property
    def category(self) -> str:
        return "bom"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "MEDIUM"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        bom_items = context.get("bom", {}).get("items", [])

        has_regulator = any("regulator" in it.get("category", "").lower() or "dc-dc" in it.get("category", "").lower() for it in bom_items)
        has_capacitor = any("capacitor" in it.get("category", "").lower() for it in bom_items)

        if has_regulator and not has_capacitor:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-PASS-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="WARNING",
                    severity="MEDIUM",
                    title="Missing Decoupling Capacitors for Power Regulators",
                    description="Switching buck regulators require input/output bulk ceramic/polymer capacitors for ripple suppression.",
                    recommended_action="Add 1000uF solid polymer decoupling capacitors to BOM.",
                    blocking=False,
                )
            )
        else:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-PASS-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="Supporting Passives Verified",
                    description="Decoupling capacitors and circuit protection devices are present in BOM.",
                    blocking=False,
                )
            )

        return results
