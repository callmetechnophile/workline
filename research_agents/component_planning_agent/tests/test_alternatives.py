"""
Unit tests for AlternativeGenerator (Sections 18 & 19).
"""

from research_agents.component_planning_agent.schemas import BOMItem, ComponentAlternativeItem
from research_agents.component_planning_agent.services.alternative_generator import AlternativeGenerator


def test_alternative_generator():
    generator = AlternativeGenerator()

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
            alternatives=[
                ComponentAlternativeItem(
                    alternative_id="ALT-001",
                    part_number="SC1111",
                    manufacturer="Raspberry Pi",
                    compatibility="architecture_alternative",
                    differences=["Lower AI compute"],
                    reason="Low-cost SBC alternative",
                    confidence=0.85,
                )
            ],
            selection_reason="AI",
        )
    ]

    alts = generator.generate_alternatives(bom_items)
    assert len(alts) == 1
    assert alts[0].part_number == "SC1111"
    assert alts[0].compatibility == "architecture_alternative"
