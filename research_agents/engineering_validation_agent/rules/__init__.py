"""Modular design rule checks for EngineeringValidationAgent."""

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

__all__ = [
    "ValidationRule",
    "LogicVoltageMismatchRule",
    "PowerLoadCapacityRule",
    "BatteryCapacityRule",
    "InterfaceProtocolMatchRule",
    "I2CAddressCollisionRule",
    "PeripheralResourceExhaustionRule",
    "MissingComponentRule",
    "QuantityConsistencyRule",
    "SupportingPassivesRule",
    "ProcurementSubstitutionRule",
    "SoftwareToolchainCompatibilityRule",
    "ThermalManagementRule",
    "MechanicalMountingRule",
]
