"""
Unit tests for SupportingPassivesIdentifier (Sections 16 & 17).
"""

from research_agents.component_planning_agent.schemas import BOMItem
from research_agents.component_planning_agent.services.supporting_passives import SupportingPassivesIdentifier


def test_supporting_passives_identification():
    identifier = SupportingPassivesIdentifier()

    primary_items = [
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
        )
    ]

    passives = identifier.identify_supporting_passives(primary_items, start_line_number=2)

    assert len(passives) >= 2
    cat_set = {p.category for p in passives}
    assert "capacitor" in cat_set
    assert "fuse" in cat_set

    cap = next(p for p in passives if p.category == "capacitor")
    assert cap.required_specifications["capacitance"] == "1000 uF"
    assert cap.subsystem_id == "SUB-003"
