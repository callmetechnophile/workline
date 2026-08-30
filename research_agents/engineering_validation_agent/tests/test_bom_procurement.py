"""
Unit tests for BOM completeness, quantities, and procurement substitution validation (Sections 26, 28, 29).
"""

from research_agents.engineering_validation_agent.services.bom_procurement_validator import BOMProcurementValidator


def test_bom_procurement_validator():
    validator = BOMProcurementValidator()

    # Missing component test
    context_missing = {
        "component_roles": [{"role_name": "thermal camera", "subsystem_id": "SUB-002"}],
        "bom": {"items": [{"bom_item_id": "BOM-01", "subsystem_id": "SUB-001", "component_name": "SBC"}]},
    }
    findings = validator.validate_bom(context_missing)
    assert any(f.status == "FAIL" and "Missing Component" in f.title for f in findings)

    # Quantity shortfall test
    context_qty = {
        "bom": {"items": [{"bom_item_id": "BOM-01", "part_number": "MOTOR-01", "quantity": 4}]},
        "optimized_procurement": {
            "orders": [{"items": [{"bom_item_id": "BOM-01", "purchased_quantity": 2}]}]
        },
    }
    qty_findings = validator.validate_bom(context_qty)
    assert any(f.status == "FAIL" and "Quantity Shortfall" in f.title for f in qty_findings)
