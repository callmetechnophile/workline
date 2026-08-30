"""
Execution repository interface and in-memory implementation for SurrealDB persistence preparation (Section 84).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from research_agents.engineering_execution_agent.schemas import (
    DelegationObject,
    EngineeringExecutionAgentOutput,
    ExecutionAuditItem,
    ExecutionGraph,
    ToolCallRecord,
)


class ExecutionRepository(ABC):
    """Abstract repository for persisting execution and audit telemetry."""

    @abstractmethod
    async def save_execution(self, output: EngineeringExecutionAgentOutput) -> str:
        """Persists the complete execution run."""
        pass

    @abstractmethod
    async def get_execution(self, execution_id: str) -> Optional[EngineeringExecutionAgentOutput]:
        """Retrieves a previously stored execution run."""
        pass

    @abstractmethod
    async def save_task_execution(self, task_data: Dict[str, Any], execution_id: str) -> None:
        """Persists granular task result."""
        pass

    @abstractmethod
    async def save_tool_call(self, tool_call: ToolCallRecord, execution_id: str) -> None:
        """Persists individual tool invocation telemetry."""
        pass

    @abstractmethod
    async def save_authorization_event(self, auth_event: Dict[str, Any], execution_id: str) -> None:
        """Persists authorization checks and denials."""
        pass

    @abstractmethod
    async def save_delegation(self, delegation: DelegationObject, execution_id: str) -> None:
        """Persists child agent delegation records."""
        pass

    @abstractmethod
    async def save_receipt(self, receipt: Dict[str, Any], execution_id: str) -> None:
        """Persists ArmorIQ cryptographic receipts."""
        pass

    @abstractmethod
    async def save_execution_graph(self, graph: ExecutionGraph, execution_id: str) -> None:
        """Persists the execution dependency graph."""
        pass

    @abstractmethod
    async def save_audit_event(self, audit_item: ExecutionAuditItem, execution_id: str) -> None:
        """Persists an execution audit record."""
        pass


class InMemoryExecutionRepository(ExecutionRepository):
    """In-memory storage implementation for local test suites and dry-run executions."""

    def __init__(self):
        self.executions: Dict[str, EngineeringExecutionAgentOutput] = {}
        self.tasks: Dict[str, List[Dict[str, Any]]] = {}
        self.tool_calls: Dict[str, List[ToolCallRecord]] = {}
        self.auth_events: Dict[str, List[Dict[str, Any]]] = {}
        self.delegations: Dict[str, List[DelegationObject]] = {}
        self.receipts: Dict[str, List[Dict[str, Any]]] = {}
        self.graphs: Dict[str, ExecutionGraph] = {}
        self.audit_trail: Dict[str, List[ExecutionAuditItem]] = {}

    async def save_execution(self, output: EngineeringExecutionAgentOutput) -> str:
        self.executions[output.execution_id] = output
        return output.execution_id

    async def get_execution(self, execution_id: str) -> Optional[EngineeringExecutionAgentOutput]:
        return self.executions.get(execution_id)

    async def save_task_execution(self, task_data: Dict[str, Any], execution_id: str) -> None:
        if execution_id not in self.tasks:
            self.tasks[execution_id] = []
        self.tasks[execution_id].append(task_data)

    async def save_tool_call(self, tool_call: ToolCallRecord, execution_id: str) -> None:
        if execution_id not in self.tool_calls:
            self.tool_calls[execution_id] = []
        self.tool_calls[execution_id].append(tool_call)

    async def save_authorization_event(self, auth_event: Dict[str, Any], execution_id: str) -> None:
        if execution_id not in self.auth_events:
            self.auth_events[execution_id] = []
        self.auth_events[execution_id].append(auth_event)

    async def save_delegation(self, delegation: DelegationObject, execution_id: str) -> None:
        if execution_id not in self.delegations:
            self.delegations[execution_id] = []
        self.delegations[execution_id].append(delegation)

    async def save_receipt(self, receipt: Dict[str, Any], execution_id: str) -> None:
        if execution_id not in self.receipts:
            self.receipts[execution_id] = []
        self.receipts[execution_id].append(receipt)

    async def save_execution_graph(self, graph: ExecutionGraph, execution_id: str) -> None:
        self.graphs[execution_id] = graph

    async def save_audit_event(self, audit_item: ExecutionAuditItem, execution_id: str) -> None:
        if execution_id not in self.audit_trail:
            self.audit_trail[execution_id] = []
        self.audit_trail[execution_id].append(audit_item)
