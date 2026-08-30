"""
Electrical domain design rules for EngineeringValidationAgent (Sections 14 & 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class LogicVoltageMismatchRule(ValidationRule):
    """RULE-ELEC-001: Verifies that digital logic levels between interconnected components match or have level shifting."""

    @property
    def rule_id(self) -> str:
        return "RULE-ELEC-001"

    @property
    def title(self) -> str:
        return "Logic Voltage Level Compatibility"

    @property
    def category(self) -> str:
        return "electrical"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "CRITICAL"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        interfaces = context.get("interfaces", [])
        bom_items = context.get("bom", {}).get("items", [])

        # Build component voltage lookup
        comp_voltages: Dict[str, float] = {}
        for it in bom_items:
            part_no = it.get("part_number", "")
            comp_name = it.get("component_name", "")
            req_specs = it.get("required_specifications", {})
            known_specs = it.get("known_specifications", {})

            v_val = req_specs.get("logic_voltage") or known_specs.get("logic_voltage") or req_specs.get("operating_voltage") or known_specs.get("operating_voltage")
            if v_val is not None:
                try:
                    comp_voltages[it.get("bom_item_id", "")] = float(str(v_val).replace("V", "").strip())
                except ValueError:
                    pass

        # Check explicit interfaces
        for iface in interfaces:
            src = iface.get("source_component_id") or iface.get("from_component")
            dst = iface.get("destination_component_id") or iface.get("to_component")
            proto = iface.get("protocol", "digital")
            level_shifted = iface.get("level_shifted", False) or iface.get("has_level_shifter", False)

            v_src = iface.get("voltage_level") or comp_voltages.get(src)
            v_dst = comp_voltages.get(dst)

            # Check if there is an explicit mismatch
            if v_src and v_dst and abs(v_src - v_dst) > 0.5 and not level_shifted:
                results.append(
                    ValidationItem(
                        validation_id=f"VAL-ELEC-{uuid.uuid4().hex[:6].upper()}",
                        rule_id=self.rule_id,
                        category=self.category,
                        status="FAIL",
                        severity="CRITICAL",
                        title=f"Logic Voltage Mismatch on {proto.upper()} ({src} -> {dst})",
                        description=(
                            f"Source component '{src}' operates at {v_src}V while destination '{dst}' "
                            f"operates at {v_dst}V without level shifting, risking input overvoltage or signal corruption."
                        ),
                        affected_components=[str(src), str(dst)],
                        affected_subsystems=[iface.get("subsystem_id", "SUB-ELEC")],
                        recommended_action=f"Insert a bidirectional logic level shifter (e.g. TXS0108E / TXB0104) between {src} ({v_src}V) and {dst} ({v_dst}V).",
                        blocking=True,
                    )
                )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-ELEC-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="Digital Logic Voltage Levels Compatible",
                    description="All evaluated digital communication buses maintain compatible 3.3V/5V logic levels or dedicated level shifting.",
                    blocking=False,
                )
            )

        return results
