"""
Unit tests for ValidationEngine and blocking verdict logic (Sections 35, 37, 38).
"""

from research_agents.engineering_validation_agent.services.rule_engine import ValidationEngine


def test_validation_engine_verdict_ready():
    engine = ValidationEngine()
    context_valid = {
        "interfaces": [{"voltage_level": 3.3}],
        "power_domains": [{"domain_name": "5V_MAIN", "max_current_capacity_a": 5.0, "known_load_current_a": 2.0}],
        "bom": {
            "items": [
                {"bom_item_id": "BOM-01", "part_number": "ESP32", "category": "microcontroller", "quantity": 1},
                {"bom_item_id": "BOM-02", "part_number": "TPS565208", "category": "DC-DC converter", "quantity": 1},
                {"bom_item_id": "BOM-03", "part_number": "CAP-1000uF", "category": "capacitor", "quantity": 1},
            ]
        },
        "optimized_procurement": {
            "orders": [{"items": [{"bom_item_id": "BOM-01", "purchased_quantity": 1}]}]
        },
    }

    findings, verdict = engine.execute_rules(context_valid)
    assert verdict.verdict == "READY"
    assert verdict.critical_failures == 0


def test_validation_engine_verdict_blocked_on_critical():
    engine = ValidationEngine()
    context_invalid = {
        "interfaces": [{"source_component_id": "BOM-01", "destination_component_id": "BOM-02", "voltage_level": 5.0}],
        "bom": {"items": [{"bom_item_id": "BOM-02", "known_specifications": {"operating_voltage": "3.3V"}}]},
    }

    findings, verdict = engine.execute_rules(context_invalid)
    assert verdict.verdict == "BLOCKED"
    assert verdict.critical_failures >= 1
