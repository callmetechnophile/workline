"""
Unit tests for ChangeRequest lifecycle and status transitions (Sections 6 & 40–42).
"""

from research_agents.engineering_change_control.schemas import ChangeRequest


def test_change_lifecycle_transitions():
    chg = ChangeRequest(
        change_id="CHG-001",
        project_id="p1",
        change_type="COMPONENT_CHANGE",
        title="Replace MCU",
        description="Upgrade STM32 to ESP32",
        status="DRAFT",
    )
    assert chg.status == "DRAFT"

    chg.status = "ANALYZING"
    assert chg.status == "ANALYZING"

    chg.status = "PENDING_APPROVAL"
    assert chg.status == "PENDING_APPROVAL"

    chg.status = "APPROVED"
    assert chg.status == "APPROVED"

    chg.status = "VERIFIED"
    assert chg.status == "VERIFIED"
