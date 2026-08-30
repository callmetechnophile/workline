"""
Integration test scenarios mandated by specification (Sections 73–80).
"""

import tempfile
from pathlib import Path
import pytest

from research_agents.verification_qa_agent.agent import VerificationQAAgent
from research_agents.verification_qa_agent.providers.mock_provider import MockQAProvider
from research_agents.verification_qa_agent.schemas import VerificationQAAgentInput


@pytest.mark.asyncio
async def test_scenario_74_full_pass():
    """Section 74: Full Pass -> VERIFIED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        (p / "firmware" / "sensors").mkdir(parents=True, exist_ok=True)
        (p / "firmware" / "sensors" / "driver.py").write_text("# clean driver\n", encoding="utf-8")

        agent = VerificationQAAgent(
            reasoning_provider=MockQAProvider(),
            project_root_dir=tmp_dir,
        )

        input_data = VerificationQAAgentInput(
            project={"title": "SAR Drone", "project_id": "proj_01"},
            implementation_plan={
                "tasks": [
                    {
                        "task_id": "TASK-001",
                        "target_file": "firmware/sensors/driver.py",
                        "acceptance_criteria": ["Sensor responds"],
                    }
                ]
            },
            execution_result={
                "completed_tasks": [{"task_id": "TASK-001"}],
                "changed_files": ["firmware/sensors/driver.py"],
                "authorized_execution": {"allowed_paths": ["firmware/**"]},
            },
            validation={"verdict": "READY"},
            dry_run=True,
        )

        output = await agent.run(input_data)
        assert output.final_verdict.verdict == "VERIFIED"
        assert output.final_verdict.security_failures == 0


@pytest.mark.asyncio
async def test_scenario_76_unknown_hardware_incomplete():
    """Section 76: Missing physical hardware -> INCOMPLETE."""
    agent = VerificationQAAgent(reasoning_provider=MockQAProvider())

    input_data = VerificationQAAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={
            "tasks": [
                {
                    "task_id": "TASK-001",
                    "acceptance_criteria": ["untested physical sensor response in field"],
                }
            ]
        },
        execution_result={"completed_tasks": [{"task_id": "TASK-001"}]},
        validation={"verdict": "READY"},
        dry_run=True,
    )

    output = await agent.run(input_data)
    assert output.final_verdict.verdict == "INCOMPLETE"


@pytest.mark.asyncio
async def test_scenario_77_out_of_scope_failed():
    """Section 77: Unauthorized file modification -> FAILED."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        (p / "backend").mkdir(parents=True, exist_ok=True)
        (p / "backend" / "evil.py").write_text("# unauthorized", encoding="utf-8")

        agent = VerificationQAAgent(
            reasoning_provider=MockQAProvider(),
            project_root_dir=tmp_dir,
        )

        input_data = VerificationQAAgentInput(
            project={"title": "SAR Drone", "project_id": "proj_01"},
            implementation_plan={"tasks": [{"task_id": "TASK-001", "target_file": "firmware/driver.py"}]},
            execution_result={
                "completed_tasks": [{"task_id": "TASK-001"}],
                "changed_files": ["backend/evil.py"],
                "authorized_execution": {"allowed_paths": ["firmware/**"]},
            },
            validation={"verdict": "READY"},
            dry_run=True,
        )

        output = await agent.run(input_data)
        assert output.final_verdict.verdict == "FAILED"
        assert output.final_verdict.scope_failures > 0


@pytest.mark.asyncio
async def test_scenario_78_security_secret_leak_failed():
    """Section 78: Hardcoded secret detected -> FAILED (with masked secret in report)."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        p = Path(tmp_dir)
        (p / "firmware").mkdir(parents=True, exist_ok=True)
        (p / "firmware" / "secret.py").write_text("AWS_SECRET_ACCESS_KEY = 'AKIA1234567890SECRETKEY'\n", encoding="utf-8")

        agent = VerificationQAAgent(
            reasoning_provider=MockQAProvider(),
            project_root_dir=tmp_dir,
        )

        input_data = VerificationQAAgentInput(
            project={"title": "SAR Drone", "project_id": "proj_01"},
            implementation_plan={"tasks": [{"task_id": "TASK-001", "target_file": "firmware/secret.py"}]},
            execution_result={
                "completed_tasks": [{"task_id": "TASK-001"}],
                "changed_files": ["firmware/secret.py"],
                "authorized_execution": {"allowed_paths": ["firmware/**"]},
            },
            validation={"verdict": "READY"},
            dry_run=True,
        )

        output = await agent.run(input_data)
        assert output.final_verdict.verdict == "FAILED"
        assert output.final_verdict.security_failures == 1
        assert len(output.security_findings) == 1
        assert "1234567890SECRETKEY" not in output.security_findings[0].masked_snippet


@pytest.mark.asyncio
async def test_scenario_79_architecture_bypass_failed():
    """Section 79: Architecture bypass -> FAILED."""
    agent = VerificationQAAgent(reasoning_provider=MockQAProvider())

    input_data = VerificationQAAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={
            "tasks": [
                {
                    "task_id": "TASK-001",
                    "title": "Bypass preprocessor layer directly to AI model",
                }
            ]
        },
        execution_result={"completed_tasks": [{"task_id": "TASK-001"}]},
        validation={"verdict": "READY"},
        dry_run=True,
    )

    output = await agent.run(input_data)
    assert output.final_verdict.verdict == "FAILED"
    assert output.final_verdict.architecture_failures == 1


@pytest.mark.asyncio
async def test_scenario_80_bom_unapproved_substitute_failed():
    """Section 80: Unapproved component substitute -> FAILED."""
    agent = VerificationQAAgent(reasoning_provider=MockQAProvider())

    input_data = VerificationQAAgentInput(
        project={"title": "SAR Drone", "project_id": "proj_01"},
        implementation_plan={
            "tasks": [
                {
                    "task_id": "TASK-001",
                    "title": "Use unapproved substitute component for IMU",
                }
            ]
        },
        execution_result={"completed_tasks": [{"task_id": "TASK-001"}]},
        validation={"verdict": "READY"},
        dry_run=True,
    )

    output = await agent.run(input_data)
    assert output.final_verdict.verdict == "FAILED"
    assert output.final_verdict.bom_failures == 1
