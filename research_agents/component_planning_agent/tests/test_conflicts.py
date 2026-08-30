"""
Unit tests for ResourceConflictDetector (Section 14).
"""

from research_agents.component_planning_agent.schemas import BOMItem
from research_agents.component_planning_agent.services.conflict_detector import ResourceConflictDetector


def test_resource_conflict_detection():
    detector = ResourceConflictDetector()

    bom_items = [
        BOMItem(
            bom_item_id="BOM-001",
            category="thermal camera",
            part_number="FLIR",
            manufacturer="FLIR",
            component_name="FLIR Lepton",
            description="Thermal",
            subsystem_id="SUB-002",
            role="sensor",
            interfaces=["SPI", "I2C"],
            selection_reason="Thermal",
        ),
        BOMItem(
            bom_item_id="BOM-002",
            category="sensor",
            part_number="BMP280",
            manufacturer="Bosch",
            component_name="BMP280 Barometer",
            description="Pressure",
            subsystem_id="SUB-002",
            role="barometer",
            interfaces=["I2C"],
            selection_reason="Altitude",
        ),
    ]

    conflicts = detector.detect_conflicts(bom_items, [])
    assert len(conflicts) >= 1
    assert conflicts[0].type == "i2c_address"
    assert "FLIR Lepton" in conflicts[0].affected_components
    assert "BMP280 Barometer" in conflicts[0].affected_components
