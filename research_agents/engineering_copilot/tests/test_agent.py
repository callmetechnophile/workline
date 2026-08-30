"""
End-to-end unit and integration tests for EngineeringCopilotAgent (Agent #15).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.engineering_copilot.agent import EngineeringCopilotAgent
from research_agents.engineering_copilot.providers.mock_provider import MockCopilotProvider
from research_agents.engineering_copilot.schemas import CopilotInput


@pytest.mark.asyncio
async def test_engineering_copilot_full_run_and_export():
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = CopilotInput(
            message="Why was the FLIR Lepton 3.5 sensor selected?",
            project_id="proj_sar_drone_001",
            user_id="user_001",
            output_dir=tmp_dir,
        )

        resp = await copilot.answer(inp)
        assert resp.project_id == "proj_sar_drone_001"
        assert len(resp.evidence) > 0
        assert len(resp.exported_files) == 7

        dir_p = Path(tmp_dir)
        assert (dir_p / "copilot_response.json").exists()
        assert (dir_p / "project_summary.json").exists()
        assert (dir_p / "traceability_response.json").exists()
        assert (dir_p / "impact_analysis.json").exists()
        assert (dir_p / "comparison.json").exists()
        assert (dir_p / "conversation.json").exists()
        assert (dir_p / "action_proposals.json").exists()


def test_engineering_copilot_sync_and_adk_capabilities():
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())

    # ADK Methods
    ans = copilot.answer_question("Why was this sensor chosen?", "proj_sar_001")
    assert ans.project_id == "proj_sar_001"

    trace = copilot.trace_requirement("REQ-SAR-001", "proj_sar_001")
    assert trace.intent == "REQUIREMENT_TRACE"

    impact = copilot.trace_component("500-0771-01", "proj_sar_001")
    assert impact.intent == "COMPONENT_IMPACT"

    status = copilot.get_project_status("proj_sar_001")
    assert status.intent == "PROJECT_STATUS"

    next_act = copilot.get_next_action("proj_sar_001")
    assert next_act.intent == "NEXT_ACTION"
