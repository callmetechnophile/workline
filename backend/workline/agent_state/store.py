"""
Durable Agent State & Checkpoint Store.
"""

import abc
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timezone
from loguru import logger

from backend.workline.agent_state.models import (
    AgentRun,
    AgentRunStatus,
    AgentCheckpoint,
    AgentDecision,
    ToolExecution,
)


class AgentStateStore(abc.ABC):
    """Abstract store interface for tracking agent runs and checkpoints."""

    @abc.abstractmethod
    async def create_run(self, run: AgentRun) -> AgentRun:
        pass

    @abc.abstractmethod
    async def get_run(self, run_id: str) -> Optional[AgentRun]:
        pass

    @abc.abstractmethod
    async def update_run(self, run: AgentRun) -> AgentRun:
        pass

    @abc.abstractmethod
    async def append_tool_execution(self, run_id: str, tool_exec: ToolExecution) -> Optional[ToolExecution]:
        pass

    @abc.abstractmethod
    async def save_checkpoint(self, checkpoint: AgentCheckpoint) -> AgentCheckpoint:
        pass

    @abc.abstractmethod
    async def get_latest_checkpoint(self, run_id: str) -> Optional[AgentCheckpoint]:
        pass

    @abc.abstractmethod
    async def record_decision(self, decision: AgentDecision) -> AgentDecision:
        pass


class LocalAgentStateStore(AgentStateStore):
    """Thread-safe in-memory/local persistent implementation of AgentStateStore."""

    def __init__(self):
        self._runs: Dict[str, AgentRun] = {}
        self._checkpoints: Dict[str, List[AgentCheckpoint]] = {}
        self._decisions: Dict[str, List[AgentDecision]] = {}
        self._lock = asyncio.Lock()

    async def create_run(self, run: AgentRun) -> AgentRun:
        async with self._lock:
            self._runs[run.run_id] = run
            self._checkpoints[run.run_id] = []
            self._decisions[run.run_id] = []
            logger.info(f"[AgentStateStore] Created agent run {run.run_id} for agent {run.agent_id}")
            return run

    async def get_run(self, run_id: str) -> Optional[AgentRun]:
        async with self._lock:
            return self._runs.get(run_id)

    async def update_run(self, run: AgentRun) -> AgentRun:
        async with self._lock:
            self._runs[run.run_id] = run
            return run

    async def append_tool_execution(self, run_id: str, tool_exec: ToolExecution) -> Optional[ToolExecution]:
        async with self._lock:
            run = self._runs.get(run_id)
            if not run:
                return None
            run.tool_executions.append(tool_exec)
            return tool_exec

    async def save_checkpoint(self, checkpoint: AgentCheckpoint) -> AgentCheckpoint:
        async with self._lock:
            if checkpoint.run_id not in self._checkpoints:
                self._checkpoints[checkpoint.run_id] = []
            self._checkpoints[checkpoint.run_id].append(checkpoint)
            run = self._runs.get(checkpoint.run_id)
            if run:
                run.checkpoints.append(checkpoint)
            logger.info(f"[AgentStateStore] Saved checkpoint {checkpoint.checkpoint_id} for run {checkpoint.run_id}")
            return checkpoint

    async def get_latest_checkpoint(self, run_id: str) -> Optional[AgentCheckpoint]:
        async with self._lock:
            chks = self._checkpoints.get(run_id, [])
            return chks[-1] if chks else None

    async def record_decision(self, decision: AgentDecision) -> AgentDecision:
        async with self._lock:
            if decision.run_id not in self._decisions:
                self._decisions[decision.run_id] = []
            self._decisions[decision.run_id].append(decision)
            run = self._runs.get(decision.run_id)
            if run:
                run.decisions.append(decision)
            return decision


default_agent_state_store = LocalAgentStateStore()
