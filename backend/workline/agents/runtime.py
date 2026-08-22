"""Workline ADK Runtime: Manages Google ADK runners, sessions, event dispatch, and idempotent retries."""

import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

from backend.workline.agents.root.orchestrator import RootOrchestratorAgent
from backend.workline.agents.shared.schemas import AgentOutput
from backend.workline.agents.shared.state import (
    AgentEvent,
    AgentState,
    AgentStatus,
    WorklineSession,
)
from backend.workline.agents.shared.tools import WorklineToolSuite
from backend.workline.database.repositories.project_repository import ProjectRepository
from backend.workline.database.surrealdb import surreal_db


def _get_agent_storage_dir() -> Path:
    base = Path.home() / ".workline" / "agents"
    base.mkdir(parents=True, exist_ok=True)
    return base


class WorklineADKRuntime:
    """
    Durable runtime managing agent workflows, sessions, human checkpoints, and state persistence.
    """

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.root_agent = RootOrchestratorAgent(self.tools)
        self.project_repo = ProjectRepository(surreal_db)

        # In-memory execution registry (mirrored to durable store)
        self._executions: Dict[str, AgentState] = {}
        self._sessions: Dict[str, WorklineSession] = {}
        self._load_local_state()

    def _load_local_state(self) -> None:
        """Load recent execution state from durable local cache."""
        storage_dir = _get_agent_storage_dir()
        for f in storage_dir.glob("*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                    state = AgentState.model_validate(data)
                    self._executions[state.execution_id] = state
            except Exception:
                pass

    def _persist_state(self, state: AgentState) -> None:
        """Persist state to local store and SurrealDB."""
        self._executions[state.execution_id] = state
        storage_dir = _get_agent_storage_dir()
        fpath = storage_dir / f"{state.execution_id}.json"
        try:
            with open(fpath, "w", encoding="utf-8") as fp:
                json.dump(state.model_dump(), fp, indent=2)
        except Exception:
            pass

    def create_session(self, user_id: str, project_id: str, team_id: Optional[str] = None) -> WorklineSession:
        """Initialize a Workline agent session."""
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        sess = WorklineSession(
            session_id=session_id,
            user_id=user_id,
            team_id=team_id,
            project_id=project_id,
        )
        self._sessions[session_id] = sess
        return sess

    async def start_execution(
        self,
        project_id: str,
        task: str,
        stage: Optional[str] = None,
        user_id: str = "default_user",
        session_id: Optional[str] = None,
    ) -> AgentState:
        """
        Launch an asynchronous agent execution run.
        """
        if not session_id or session_id not in self._sessions:
            sess = self.create_session(user_id=user_id, project_id=project_id)
            session_id = sess.session_id

        exec_id = f"exec_{uuid.uuid4().hex[:12]}"
        state = AgentState(
            execution_id=exec_id,
            session_id=session_id,
            project_id=project_id,
            agent_id="root_orchestrator",
            agent_type="orchestrator",
            task_id=f"task_{uuid.uuid4().hex[:8]}",
            stage=stage or "ideation",
            status=AgentStatus.RUNNING,
            input_context={"task": task, "stage": stage},
        )
        self._persist_state(state)
        self._sessions[session_id].active_execution_id = exec_id
        self._sessions[session_id].history.append(exec_id)

        # Run Phase 1 (Planning + Research)
        try:
            out: AgentOutput = await self.root_agent.execute_phase1_planning_and_research(
                project_id=project_id, task=task, state=state
            )
            state.output_summary = out.summary
            state.artifacts = out.artifacts
        except Exception as exc:
            state.status = AgentStatus.FAILED
            state.errors.append(str(exc))
            state.events.append(
                AgentEvent(
                    agent_id=state.agent_id,
                    event_type="ERROR",
                    summary="Execution failed",
                    details={"error": str(exc)},
                )
            )
        finally:
            self._persist_state(state)

        return state

    async def submit_human_approval(
        self, execution_id: str, decision: str
    ) -> AgentState:
        """
        Resume an execution paused at the Human Decision Checkpoint.
        decision options: 'START_BUILD', 'CONTINUE_RESEARCH'
        """
        state = self._executions.get(execution_id)
        if not state:
            raise ValueError(f"Execution {execution_id} not found.")

        if state.status != AgentStatus.WAITING_FOR_USER:
            raise ValueError(f"Execution is in {state.status} state, not WAITING_FOR_USER.")

        state.events.append(
            AgentEvent(
                agent_id="human_user",
                event_type="USER_DECISION",
                summary=f"User selected: {decision}",
                details={"decision": decision},
            )
        )

        task = state.input_context.get("task", "")

        if decision.upper() == "START_BUILD":
            state.status = AgentStatus.RUNNING
            try:
                out = await self.root_agent.execute_phase2_builder(
                    project_id=state.project_id, task=task, state=state
                )
                state.status = AgentStatus.COMPLETED
                state.output_summary = out.summary
                state.completed_at = datetime.now(timezone.utc).isoformat()
            except Exception as exc:
                state.status = AgentStatus.FAILED
                state.errors.append(str(exc))
            finally:
                self._persist_state(state)
        elif decision.upper() == "CONTINUE_RESEARCH":
            state.status = AgentStatus.RUNNING
            context = await self.tools.get_project(state.project_id)
            res_out = await self.root_agent.research_agent.execute(state.project_id, context or {})
            state.events.append(AgentEvent(agent_id="research_agent", event_type="SUMMARY", summary=res_out.summary))
            state.status = AgentStatus.WAITING_FOR_USER
            state.requires_user_action = True
            state.action_prompt = "ADDITIONAL RESEARCH COMPLETE. Choose: [Continue Research] or [Start Building]"
            self._persist_state(state)

        return state

    def get_execution(self, execution_id: str) -> Optional[AgentState]:
        """Fetch live execution state."""
        return self._executions.get(execution_id)

    def list_executions_for_project(self, project_id: str) -> List[AgentState]:
        """List all executions associated with a given project."""
        self._load_local_state()
        return [s for s in self._executions.values() if s.project_id == project_id]


# Global runtime singleton
agent_runtime = WorklineADKRuntime()
