"""
End-to-end unit and integration tests for EngineeringChangeControlAgent (Agent #16).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.engineering_change_control.agent import EngineeringChangeControlAgent
from research_agents.engineering_change_control.providers.mock_provider import MockChangeControlProvider
from research_agents.engineering_change_control.schemas import ChangeControlInput


@pytest.mark.asyncio
async def test_change_control_full_run_and_export():
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = ChangeControlInput(
            project_id="proj_sar_drone_001",
            change_type="COMPONENT_CHANGE",
            title="Replace Thermal Sensor Core",
            description="Upgrade to radiometric FLIR Lepton 3.5.",
            target_artifact="500-0771-01",
            user_id="user_001",
            output_dir=tmp_dir,
        )

        out = await agent.process_change_request(inp)
        assert out.change_request.project_id == "proj_sar_drone_001"
        assert len(out.exported_files) == 5

        dir_p = Path(tmp_dir)
        assert (dir_p / "change_request.json").exists()
        assert (dir_p / "change_impact.json").exists()
        assert (dir_p / "change_risks.json").exists()
        assert (dir_p / "change_plan.json").exists()
        assert (dir_p / "change_report.md").exists()


def test_change_control_sync_and_adk_capabilities():
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())

    # ADK Methods
    out = agent.create_change(
        project_id="proj_sar_001",
        change_type="COMPONENT_CHANGE",
        title="Swap Sensor Core",
        description="Upgrade",
        target_artifact="500-0771-01",
    )
    assert out.change_request.change_id.startswith("CHANGE-")

    # Rollback
    rollback, new_ver = agent.execute_rollback(
        artifact_id="ARCH-001",
        target_version="v1.0.0",
        current_version="v2.0.0",
        approved_by="lead_bob",
    )
    assert rollback.rollback_id.startswith("ROLL-")
    assert new_ver.version == "v3.0.0"
