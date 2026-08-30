"""
Unit tests for ComponentSelector (Sections 8, 9, 10, 20).
"""

from research_agents.component_planning_agent.schemas import ComponentRequirementItem
from research_agents.component_planning_agent.services.component_selector import ComponentSelector


def test_component_selection_and_specification_separation():
    selector = ComponentSelector()

    comp_reqs = [
        ComponentRequirementItem(
            requirement_id="REQ-001",
            category="SBC",
            quantity=1,
            required_specifications={"ai_compute": ">= 40 TOPS"},
            source_subsystem="SUB-001",
            reason="AI host",
        ),
        ComponentRequirementItem(
            requirement_id="REQ-002",
            category="thermal camera",
            quantity=1,
            required_specifications={"resolution": ">= 160x120"},
            source_subsystem="SUB-002",
            reason="Thermal imaging",
        ),
    ]

    items = selector.select_components(comp_reqs, [], [])

    assert len(items) == 2
    jetson_item = next(i for i in items if i.category == "SBC")
    assert jetson_item.manufacturer == "NVIDIA"
    assert jetson_item.part_number == "900-13766-0000-000"
    assert jetson_item.selection_status == "selected"
    assert "ai_compute" in jetson_item.required_specifications
    assert "ai_compute" in jetson_item.known_specifications
    assert jetson_item.datasheet_url is not None
    assert "nvidia.com" in jetson_item.datasheet_url
