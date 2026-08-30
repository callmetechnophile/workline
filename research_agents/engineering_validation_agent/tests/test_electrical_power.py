"""
Unit tests for electrical and power domain validation services (Sections 14, 15, 16).
"""

from research_agents.engineering_validation_agent.services.electrical_validator import ElectricalValidator
from research_agents.engineering_validation_agent.services.power_validator import PowerValidator


def test_electrical_validator():
    validator = ElectricalValidator()
    context_fail = {
        "interfaces": [{"source_component_id": "MCU", "destination_component_id": "SENSOR", "voltage_level": 5.0}],
        "bom": {"items": [{"bom_item_id": "SENSOR", "known_specifications": {"operating_voltage": "3.3V"}}]},
    }
    findings = validator.validate_electrical(context_fail)
    assert any(f.status == "FAIL" for f in findings)


def test_power_validator_overcurrent():
    validator = PowerValidator()
    context = {
        "power_domains": [{"domain_name": "5V_MAIN", "max_current_capacity_a": 2.0}],
        "bom": {"items": [{"power_domain": "5V_MAIN", "known_specifications": {"max_current_draw": "3.0A"}}]},
    }
    findings = validator.validate_power(context)
    assert any(f.status == "FAIL" and f.severity == "CRITICAL" for f in findings)
