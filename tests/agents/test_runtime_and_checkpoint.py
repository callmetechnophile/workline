"""Tests for ADK Runtime, sessions, human checkpoints, and state recovery."""

import asyncio
import pytest
from backend.workline.agents.runtime import WorklineADKRuntime
from backend.workline.agents.shared.state import AgentStatus


def test_adk_runtime_session_and_checkpoint():
    """Test session creation, Phase 1 execution, WAITING_FOR_USER pause, and approval."""
    async def _run():
        runtime = WorklineADKRuntime()
        sess = runtime.create_session(user_id="lead_eng", project_id="solar_drone")
        assert sess.session_id.startswith("session_")

        # 1. Start Execution (Planning + Research)
        state = await runtime.start_execution(
            project_id="solar_drone",
            task="Design a solar-powered surveillance drone",
            session_id=sess.session_id,
        )

        assert state.status == AgentStatus.WAITING_FOR_USER
        assert state.requires_user_action is True
        assert "RESEARCH COMPLETE" in state.action_prompt
        assert len(state.events) >= 4

        # 2. Submit Human Approval: START_BUILD
        approved_state = await runtime.submit_human_approval(
            execution_id=state.execution_id,
            decision="START_BUILD",
        )

        assert approved_state.status == AgentStatus.COMPLETED
        assert approved_state.stage == "hardware_build_complete"
        assert approved_state.requires_user_action is False

    asyncio.run(_run())


def test_checkpoint_continue_research():
    """Test human decision requesting additional research iteration."""
    async def _run():
        runtime = WorklineADKRuntime()
        state = await runtime.start_execution(
            project_id="solar_drone_2",
            task="Investigate high-efficiency MPPT topologies",
        )
        assert state.status == AgentStatus.WAITING_FOR_USER

        state_more_res = await runtime.submit_human_approval(
            execution_id=state.execution_id,
            decision="CONTINUE_RESEARCH",
        )
        assert state_more_res.status == AgentStatus.WAITING_FOR_USER
        assert state_more_res.requires_user_action is True

    asyncio.run(_run())
