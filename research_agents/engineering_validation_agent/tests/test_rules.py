"""
Unit tests for individual modular design rule checks (Section 34).
"""

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
from research_agents.engineering_validation_agent.rules.power_rules import (
    BatteryCapacityRule,
    PowerLoadCapacityRule,
)
from research_agents.engineering_validation_agent.rules.procurement_rules import ProcurementSubstitutionRule


def test_logic_voltage_mismatch_rule():
    rule = LogicVoltageMismatchRule()

    # Mismatch context: 5V into 3.3V
    context_fail = {
        "interfaces": [{"source_component_id": "BOM-01", "destination_component_id": "BOM-02", "voltage_level": 5.0}],
        "bom": {"items": [{"bom_item_id": "BOM-02", "known_specifications": {"operating_voltage": "3.3V"}}]},
    }
    findings_fail = rule.check(context_fail)
    assert any(f.status == "FAIL" and f.severity == "CRITICAL" and f.blocking for f in findings_fail)

    # Compatible context
    context_pass = {
        "interfaces": [{"source_component_id": "BOM-01", "destination_component_id": "BOM-02", "voltage_level": 3.3}],
        "bom": {"items": [{"bom_item_id": "BOM-02", "known_specifications": {"operating_voltage": "3.3V"}}]},
    }
    findings_pass = rule.check(context_pass)
    assert all(f.status == "PASS" for f in findings_pass)


def test_power_load_capacity_rule():
    rule = PowerLoadCapacityRule()

    # Overload context: 2.8A load on 2.0A max regulator
    context_overload = {
        "power_domains": [{"domain_name": "5V_MAIN", "max_current_capacity_a": 2.0}],
        "bom": {
            "items": [
                {"bom_item_id": "BOM-01", "power_domain": "5V_MAIN", "known_specifications": {"max_current_draw": "2.8A"}}
            ]
        },
    }
    findings_overload = rule.check(context_overload)
    assert any(f.status == "FAIL" and f.severity == "CRITICAL" and f.blocking for f in findings_overload)


def test_i2c_address_collision_rule():
    rule = I2CAddressCollisionRule()

    context_collision = {
        "bom": {
            "items": [
                {"bom_item_id": "BOM-01", "part_number": "SENSOR-A", "known_specifications": {"i2c_address": "0x68"}},
                {"bom_item_id": "BOM-02", "part_number": "SENSOR-B", "known_specifications": {"i2c_address": "0x68"}},
            ]
        }
    }
    findings = rule.check(context_collision)
    assert any(f.status == "FAIL" and "Collision" in f.title for f in findings)


def test_procurement_substitution_rule():
    rule = ProcurementSubstitutionRule()

    context_viol = {
        "substitution_violation": {
            "substituted_part": "UART-MODULE",
            "required_part": "CAN-TRANSCEIVER",
            "reason": "Substituted component lacks required CAN interface.",
        }
    }
    findings = rule.check(context_viol)
    assert any(f.status == "FAIL" and f.severity == "CRITICAL" for f in findings)
