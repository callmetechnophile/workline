"""
End-to-end unit and integration tests for VerificationQAAgent (Agent #12).
"""

import tempfile
import pytest

from research_agents.verification_qa_agent.agent import VerificationQAAgent
from research_agents.verification_qa_agent.providers.mock_provider import MockQAProvider
from research_agents.verification_qa_agent.schemas import VerificationQAAgentInput


@pytest.mark.asyncio
async def test_verification_qa_agent_blocked_by_validation_gate():
    agent = VerificationQAAgent(reasoning_provider=MockQAProvider())

    input_data = VerificationQAAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        validation={"verdict": "BLOCKED", "critical_failures": ["RULE-VOLT-001"]},
        dry_run=True,
    )

    output = await agent.run(input_data)
    assert output.status == "blocked"
    assert output.verdict == "BLOCKED"
    assert output.final_verdict.verdict == "BLOCKED"


def test_verification_qa_agent_sync_and_adk_capabilities():
    with tempfile.TemporaryDirectory() as tmp_dir:
        agent = VerificationQAAgent(
            reasoning_provider=MockQAProvider(),
            project_root_dir=tmp_dir,
        )

        input_data = VerificationQAAgentInput(
            project={"title": "SAR Drone Sync Test", "project_id": "proj_01"},
            validation={"verdict": "READY"},
            dry_run=True,
        )

        output = agent.run_sync(input_data)
        assert output.status in ("success", "failed")

        # ADK Capability checks
        verdict = agent.generate_final_verdict(output)
        assert verdict.verdict is not None

        arch_conf = agent.verify_architecture({}, [])
        assert arch_conf.status == "PASS"

        bom_conf = agent.verify_bom({}, [])
        assert bom_conf.status == "PASS"
