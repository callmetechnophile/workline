"""
Unit tests for BOMRepository interface (Section 41).
"""

import pytest
from research_agents.component_planning_agent.repository import InMemoryBOMRepository
from research_agents.component_planning_agent.schemas import (
    BOMItem,
    BOMValidationItem,
    ComponentAlternativeItem,
    ComponentPlanningAgentOutput,
    ComponentRequirementItem,
)


@pytest.mark.asyncio
async def test_bom_repository_all_methods():
    repo = InMemoryBOMRepository()
    proj_id = "proj_test_bom_01"

    # 1. Save BOM Item
    await repo.save_bom_item(
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
        proj_id,
    )

    # 2. Save Component Requirement
    await repo.save_component_requirement(
        ComponentRequirementItem(
            requirement_id="REQ-01",
            category="SBC",
            quantity=1,
            required_specifications={"ai": "40 TOPS"},
            source_subsystem="SUB-001",
            reason="AI",
        ),
        proj_id,
    )

    # 3. Save Component Alternative
    await repo.save_component_alternative(
        ComponentAlternativeItem(
            alternative_id="ALT-01",
            part_number="SC1111",
            manufacturer="RPi",
            compatibility="architecture_alternative",
            reason="Low cost",
        ),
        proj_id,
    )

    # 4. Save BOM Validation
    await repo.save_bom_validation(
        BOMValidationItem(
            validation_id="VAL-01",
            type="electrical",
            description="Test",
            reason="Check",
        ),
        proj_id,
    )

    # 5. Save Graph Relationship
    await repo.save_bom_relationship("node_a", "node_b", "powered_by")

    # 6. Save Full Output
    output = ComponentPlanningAgentOutput(
        bom_id="BOM-001",
        project_id=proj_id,
    )
    saved_id = await repo.save_bom(output)
    assert saved_id == proj_id

    retrieved = await repo.get_bom(proj_id)
    assert retrieved is not None
    assert retrieved.bom_id == "BOM-001"
