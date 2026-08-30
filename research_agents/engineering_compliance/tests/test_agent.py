"""
End-to-end integration and ADK capability tests for EngineeringComplianceAgent (Agent #17).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.engineering_compliance.agent import EngineeringComplianceAgent
from research_agents.engineering_compliance.providers.mock_provider import MockComplianceProvider
from research_agents.engineering_compliance.schemas import ComplianceInput


@pytest.mark.asyncio
async def test_compliance_agent_full_run_and_export():
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = ComplianceInput(
            project_id="proj_sar_drone_001",
            user_id="user_001",
            output_dir=tmp_dir,
        )
        out = await agent.evaluate_compliance(inp)

        assert out.summary.project_id == "proj_sar_drone_001"
        assert len(out.exported_files) == 6

        dir_p = Path(tmp_dir)
        assert (dir_p / "compliance_summary.json").exists()
        assert (dir_p / "compliance_results.json").exists()
        assert (dir_p / "compliance_matrix.json").exists()
        assert (dir_p / "compliance_waivers.json").exists()
        assert (dir_p / "compliance_gate.json").exists()
        assert (dir_p / "compliance_report.md").exists()


def test_compliance_agent_sync_and_adk_capabilities():
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())

    # ADK Methods
    out = agent.evaluate_project("proj_sar_drone_001")
    assert out.summary.gate == "ALLOW"

    gate = agent.get_compliance_gate("proj_sar_drone_001")
    assert gate == "ALLOW"

    waiver = agent.create_waiver_request(
        project_id="proj_sar_drone_001",
        rule_id="RULE-ELEC-01",
        artifact_id="component:500-0771-01",
        reason="Test waiver",
        risk="Low",
        approved_by="officer",
    )
    assert waiver.waiver_id.startswith("WAIV-")
