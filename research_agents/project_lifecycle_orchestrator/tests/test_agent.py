"""
End-to-end unit and integration tests for ProjectLifecycleOrchestrator (Agent #14).
"""

import tempfile
from pathlib import Path
import pytest
from research_agents.project_lifecycle_orchestrator.agent import ProjectLifecycleOrchestrator
from research_agents.project_lifecycle_orchestrator.providers.mock_provider import MockOrchestratorProvider
from research_agents.project_lifecycle_orchestrator.schemas import OrchestrationInput


@pytest.mark.asyncio
async def test_project_lifecycle_orchestrator_full_run_and_export():
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())

    with tempfile.TemporaryDirectory() as tmp_dir:
        inp = OrchestrationInput(
            project_id="proj_sar_drone_001",
            user_id="user_001",
            output_dir=tmp_dir,
        )

        out = await orchestrator.run(inp, qa_status="VERIFIED", validation_status="READY")
        assert out.run.project_id == "proj_sar_drone_001"
        assert out.next_action.action_type == "COMPLETE"
        assert len(out.exported_files) == 8

        dir_p = Path(tmp_dir)
        assert (dir_p / "orchestration_run.json").exists()
        assert (dir_p / "project_health.json").exists()
        assert (dir_p / "next_action.json").exists()
        assert (dir_p / "decision_history.json").exists()
        assert (dir_p / "blockers.json").exists()
        assert (dir_p / "human_requests.json").exists()
        assert (dir_p / "state_transitions.json").exists()
        assert (dir_p / "orchestration_report.md").exists()


def test_project_lifecycle_orchestrator_sync_and_adk_capabilities():
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())
    inp = OrchestrationInput(project_id="proj_adk_001")
    out = orchestrator.run_sync(inp)

    assert out.run.project_id == "proj_adk_001"

    # Test ADK methods
    state = orchestrator.evaluate_state("proj_adk_001")
    assert state == "QA"

    next_act = orchestrator.determine_next_action("proj_adk_001", "QA")
    assert next_act is not None

    routed = orchestrator.route_to_agent("RESEARCH")
    assert routed == "ResearchPaperAgent"

    health = orchestrator.get_project_health("proj_adk_001")
    assert health.health in ("healthy", "warning", "blocked")
