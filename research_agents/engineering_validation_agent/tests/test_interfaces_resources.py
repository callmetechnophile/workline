"""
Unit tests for interface protocols and peripheral resource capacity (Sections 18, 19, 20).
"""

from research_agents.engineering_validation_agent.services.interface_validator import InterfaceValidator


def test_interface_and_resource_validator():
    validator = InterfaceValidator()

    # I2C Collision test
    context_i2c = {
        "interfaces": [{"protocol": "I2C"}],
        "bom": {
            "items": [
                {"bom_item_id": "BOM-01", "known_specifications": {"i2c_address": "0x76"}},
                {"bom_item_id": "BOM-02", "known_specifications": {"i2c_address": "0x76"}},
            ]
        },
    }
    findings = validator.validate_interfaces(context_i2c)
    assert any(f.status == "FAIL" and "Collision" in f.title for f in findings)

    # Resource exhaustion test
    context_res = {
        "interfaces": [{"protocol": "UART"}, {"protocol": "UART"}, {"protocol": "UART"}, {"protocol": "UART"}, {"protocol": "UART"}]
    }
    res_findings = validator.validate_resources(context_res)
    assert any(f.status == "WARNING" for f in res_findings)
