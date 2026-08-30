"""
Interface and resource verification service for EngineeringValidationAgent (Sections 18, 19, 20).
"""

from typing import Any, Dict, List
from research_agents.engineering_validation_agent.rules.interface_rules import (
    I2CAddressCollisionRule,
    InterfaceProtocolMatchRule,
)
from research_agents.engineering_validation_agent.rules.resource_rules import PeripheralResourceExhaustionRule
from research_agents.engineering_validation_agent.schemas import ValidationItem


class InterfaceValidator:
    """Evaluates protocol compatibility, I2C address sharing, and MCU pin/bus resource allocations."""

    def __init__(
        self,
        proto_rule: InterfaceProtocolMatchRule = None,
        i2c_rule: I2CAddressCollisionRule = None,
        res_rule: PeripheralResourceExhaustionRule = None,
    ):
        self.proto_rule = proto_rule or InterfaceProtocolMatchRule()
        self.i2c_rule = i2c_rule or I2CAddressCollisionRule()
        self.res_rule = res_rule or PeripheralResourceExhaustionRule()

    def validate_interfaces(self, context: Dict[str, Any]) -> List[ValidationItem]:
        results: List[ValidationItem] = []
        results.extend(self.proto_rule.check(context))
        results.extend(self.i2c_rule.check(context))
        return results

    def validate_resources(self, context: Dict[str, Any]) -> List[ValidationItem]:
        return self.res_rule.check(context)
