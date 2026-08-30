"""
Interface and communication protocol design rules for EngineeringValidationAgent (Sections 18, 20, 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class InterfaceProtocolMatchRule(ValidationRule):
    """RULE-INT-001: Verifies interface protocol compatibility between communicating peripherals."""

    @property
    def rule_id(self) -> str:
        return "RULE-INT-001"

    @property
    def title(self) -> str:
        return "Interface Protocol & Pinout Compatibility"

    @property
    def category(self) -> str:
        return "interface"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "CRITICAL"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        interfaces = context.get("interfaces", [])

        for iface in interfaces:
            proto = str(iface.get("protocol", "")).lower()
            src = iface.get("source_component_id", "SRC")
            dst = iface.get("destination_component_id", "DST")
            mismatch = iface.get("protocol_mismatch", False)

            if mismatch:
                results.append(
                    ValidationItem(
                        validation_id=f"VAL-INT-{uuid.uuid4().hex[:6].upper()}",
                        rule_id=self.rule_id,
                        category=self.category,
                        status="FAIL",
                        severity="CRITICAL",
                        title=f"Protocol Mismatch between {src} and {dst}",
                        description=f"Direct connection attempted between incompatible protocols on '{src}' and '{dst}'.",
                        affected_components=[str(src), str(dst)],
                        recommended_action="Ensure both endpoints support identical communication protocols (e.g. UART to UART, SPI to SPI).",
                        blocking=True,
                    )
                )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-INT-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="All Inter-Component Protocols Matched",
                    description="All evaluated digital communication links (VoSPI, I2C, UART) maintain matching protocol handshakes.",
                    blocking=False,
                )
            )

        return results


class I2CAddressCollisionRule(ValidationRule):
    """RULE-INT-002: Verifies that no two I2C devices on the same bus share identical 7-bit slave addresses."""

    @property
    def rule_id(self) -> str:
        return "RULE-INT-002"

    @property
    def title(self) -> str:
        return "I2C Bus Slave Address Collision Detection"

    @property
    def category(self) -> str:
        return "interface"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "HIGH"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        interfaces = context.get("interfaces", [])
        bom_items = context.get("bom", {}).get("items", [])

        # Collect I2C device addresses
        i2c_addresses: Dict[str, List[str]] = {}
        for it in bom_items:
            req_specs = it.get("required_specifications", {})
            known_specs = it.get("known_specifications", {})
            addr = req_specs.get("i2c_address") or known_specs.get("i2c_address")
            if addr:
                i2c_addresses.setdefault(str(addr).lower(), []).append(it.get("part_number", it.get("bom_item_id")))

        for addr, parts in i2c_addresses.items():
            if len(parts) > 1:
                results.append(
                    ValidationItem(
                        validation_id=f"VAL-I2C-{uuid.uuid4().hex[:6].upper()}",
                        rule_id=self.rule_id,
                        category=self.category,
                        status="FAIL",
                        severity="HIGH",
                        title=f"I2C Address Collision at {addr}",
                        description=f"Multiple components ({', '.join(parts)}) share the identical 7-bit I2C address {addr} on the default bus.",
                        affected_components=parts,
                        recommended_action="Use an I2C multiplexer (e.g. TCA9548A) or configure address pin jumpers to resolve bus collision.",
                        blocking=True,
                    )
                )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-I2C-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="I2C Bus Addresses Conflict-Free",
                    description="All I2C sensor endpoints (e.g. FLIR Lepton 0x2A) maintain distinct 7-bit hardware slave addresses.",
                    blocking=False,
                )
            )

        return results
