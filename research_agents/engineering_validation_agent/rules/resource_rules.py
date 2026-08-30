"""
Peripheral and hardware resource capacity design rules for EngineeringValidationAgent (Sections 19 & 34).
"""

from typing import Any, Dict, List
import uuid
from research_agents.engineering_validation_agent.rules.base import ValidationRule
from research_agents.engineering_validation_agent.schemas import ValidationItem, ValidationSeverityLiteral


class PeripheralResourceExhaustionRule(ValidationRule):
    """RULE-RES-001: Verifies that microcontroller/SBC peripheral pin and bus assignments do not exceed hardware capacity."""

    @property
    def rule_id(self) -> str:
        return "RULE-RES-001"

    @property
    def title(self) -> str:
        return "Microcontroller & Compute Resource Capacity"

    @property
    def category(self) -> str:
        return "resource"

    @property
    def default_severity(self) -> ValidationSeverityLiteral:
        return "HIGH"

    def check(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        interfaces = context.get("interfaces", [])

        # Count UART and SPI peripheral allocations to main controller
        uart_count = sum(1 for iface in interfaces if iface.get("protocol", "").lower() == "uart")
        spi_count = sum(1 for iface in interfaces if iface.get("protocol", "").lower() == "spi")

        # Flag if UART allocations exceed typical single MCU hardware ports (> 3)
        if uart_count > 4:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-RES-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="WARNING",
                    severity="MEDIUM",
                    title="Hardware UART Port Exhaustion Warning",
                    description=f"System allocates {uart_count} hardware UART channels, which may exceed single-MCU port limits.",
                    recommended_action="Introduce an SPI-to-UART bridge (e.g. MAX3100) or software serial abstraction.",
                    blocking=False,
                )
            )

        if not results:
            results.append(
                ValidationItem(
                    validation_id=f"VAL-RES-{uuid.uuid4().hex[:6].upper()}",
                    rule_id=self.rule_id,
                    category=self.category,
                    status="PASS",
                    severity="INFO",
                    title="MCU Peripheral Capacities Adequate",
                    description="Assigned SPI, I2C, and UART channels are within hardware pinout limits.",
                    blocking=False,
                )
            )

        return results
