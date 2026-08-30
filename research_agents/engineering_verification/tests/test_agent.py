"""
End-to-end integration and ADK capability tests for EngineeringVerificationAgent (Agent #18).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.engineering_verification.agent import EngineeringVerificationAgent
from research_agents.engineering_verification.providers.mock_provider import MockVerificationProvider
from research_agents.engineering_verification.schemas import VerificationInput


@pytest.mark.asyncio
async def test_verification_agent_full_run_and_export():
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = VerificationInput(
            project_id="proj_sar_drone_001",
            user_id="user_001",
            output_dir=tmp_dir,
        )
        out = await agent.execute_verification_cycle(inp)

        assert out.plan.project_id == "proj_sar_drone_001"
        assert len(out.exported_files) == 6

        dir_p = Path(tmp_dir)
        assert (dir_p / "verification_plan.json").exists()
        assert (dir_p / "verification_report.json").exists()
        assert (dir_p / "verification_matrix.json").exists()
        assert (dir_p / "test_results.json").exists()
        assert (dir_p / "evidence_index.json").exists()
        assert (dir_p / "verification_report.md").exists()


def test_verification_agent_sync_and_adk_capabilities():
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())

    # ADK Methods
    plan = agent.create_verification_plan("proj_sar_drone_001")
    assert plan.verification_plan_id.startswith("PLAN-VERIF-")

    cov = agent.get_coverage("proj_sar_drone_001")
    assert cov.coverage_percentage >= 0.0

    res = agent.execute_test("TEST-SAR-001", "proj_sar_drone_001", {"voltage": 3.28})
    assert res.status == "PASS"
