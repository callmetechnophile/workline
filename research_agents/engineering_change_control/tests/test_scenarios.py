"""
Specification-mandated test scenarios for EngineeringChangeControlAgent (Sections 79–91).
"""

import pytest
from research_agents.engineering_change_control.agent import EngineeringChangeControlAgent
from research_agents.engineering_change_control.providers.mock_provider import MockChangeControlProvider
from research_agents.engineering_change_control.schemas import ChangeControlInput


@pytest.mark.asyncio
async def test_scenario_79_component_change():
    """Section 79: Component replacement identifies BOM, subsystem, task, and validation impact."""
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())
    inp = ChangeControlInput(
        project_id="proj_sar_001",
        change_type="COMPONENT_CHANGE",
        title="Replace FLIR Lepton 2.5 with 3.5",
        description="Upgrade to radiometric core.",
        target_artifact="500-0771-01",
    )
    out = await agent.process_change_request(inp)

    assert len(out.impact.direct_impact) > 0
    assert "BOM" in out.impact.revalidation_required
    assert "VALIDATION" in out.impact.revalidation_required
    assert "QA" in out.impact.revalidation_required


@pytest.mark.asyncio
async def test_scenario_80_readme_change():
    """Section 80: Documentation change severity is LOW and requires zero engineering revalidation."""
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())
    inp = ChangeControlInput(
        project_id="proj_sar_001",
        change_type="DOCUMENTATION_CHANGE",
        title="Update README wording",
        description="Clarify developer quickstart instructions.",
        target_artifact="README.md",
    )
    out = await agent.process_change_request(inp)

    assert out.change_request.severity == "LOW"
    assert len(out.impact.revalidation_required) == 0


@pytest.mark.asyncio
async def test_scenario_81_architecture_change():
    """Section 81: Architecture change triggers full downstream revalidation."""
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())
    inp = ChangeControlInput(
        project_id="proj_sar_001",
        change_type="ARCHITECTURE_CHANGE",
        title="Revise VoSPI Bus Interface",
        description="Upgrade SPI bus timing to 15 FPS.",
        target_artifact="ARCH-001",
    )
    out = await agent.process_change_request(inp)

    assert "ARCHITECTURE" in out.impact.revalidation_required
    assert "BOM" in out.impact.revalidation_required
    assert "VALIDATION" in out.impact.revalidation_required
    assert "QA" in out.impact.revalidation_required


@pytest.mark.asyncio
async def test_scenario_83_qa_invalidation():
    """Section 83: Modifying validated architecture invalidates previous QA PASS results."""
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())
    inp = ChangeControlInput(
        project_id="proj_sar_001",
        change_type="ARCHITECTURE_CHANGE",
        title="Bus Architecture Redesign",
        description="Major bus interface change.",
        target_artifact="ARCH-001",
    )
    out = await agent.process_change_request(inp)

    assert len(out.impact.invalidated_artifacts) > 0
    assert any("qa_verdict" in inv for inv in out.impact.invalidated_artifacts)


@pytest.mark.asyncio
async def test_scenario_88_armoriq_authorization():
    """Section 88: Approved change implementation requires ArmorIQ cryptographic authority."""
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())
    inp = ChangeControlInput(
        project_id="proj_sar_001",
        change_type="COMPONENT_CHANGE",
        title="Replace sensor",
        description="Requires driver file modification.",
        target_artifact="500-0771-01",
    )
    out = await agent.process_change_request(inp)

    assert out.change_plan is not None
    assert "filesystem.write" in out.change_plan.required_authorization
