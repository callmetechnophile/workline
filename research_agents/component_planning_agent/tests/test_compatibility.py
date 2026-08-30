"""
Unit tests for CompatibilityValidator (Sections 11-13, 29, 30).
"""

from research_agents.component_planning_agent.schemas import BOMItem
from research_agents.component_planning_agent.services.compatibility_validator import CompatibilityValidator


def test_multi_domain_compatibility_validation():
    validator = CompatibilityValidator()

    bom_items = [
        BOMItem(
            bom_item_id="BOM-001",
            category="SBC",
            part_number="Jetson",
            manufacturer="NVIDIA",
            component_name="Jetson",
            description="AI",
            subsystem_id="SUB-001",
            role="compute",
            selection_reason="AI",
        ),
        BOMItem(
            bom_item_id="BOM-002",
            category="thermal camera",
            part_number="FLIR",
            manufacturer="FLIR",
            component_name="Lepton",
            description="Sensor",
            subsystem_id="SUB-002",
            role="sensor",
            selection_reason="Thermal",
        ),
    ]

    checks = validator.validate_compatibility(bom_items, [], [])

    assert len(checks) >= 4
    check_types = {c.type for c in checks}
    assert "electrical" in check_types
    assert "power" in check_types
    assert "interface" in check_types
    assert "software" in check_types

    elec_check = next(c for c in checks if c.type == "electrical")
    assert elec_check.status == "passed"
    assert "BOM-001" in elec_check.affected_items
