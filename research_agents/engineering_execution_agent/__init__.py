"""
EngineeringExecutionAgent — Agent #11 of WorkflowGuide AI Platform.
"""

from research_agents.engineering_execution_agent.agent import EngineeringExecutionAgent
from research_agents.engineering_execution_agent.armoriq.client import ArmorIQClient
from research_agents.engineering_execution_agent.armoriq.mock_client import MockArmorIQClient
from research_agents.engineering_execution_agent.config import exec_config
from research_agents.engineering_execution_agent.schemas import (
    AuthorizedExecution,
    DelegationObject,
    EngineeringExecutionContext,
    EngineeringExecutionAgentInput,
    EngineeringExecutionAgentOutput,
    ExecutionAuditItem,
    ExecutionGraph,
    ExecutionReceipt,
    ExecutionStatusLiteral,
    ExecutionTask,
    OperationTypeLiteral,
    ToolCallRecord,
    ToolTypeLiteral,
)

__all__ = [
    "EngineeringExecutionAgent",
    "ArmorIQClient",
    "MockArmorIQClient",
    "AuthorizedExecution",
    "ExecutionTask",
    "ToolCallRecord",
    "ExecutionReceipt",
    "ExecutionAuditItem",
    "ExecutionGraph",
    "DelegationObject",
    "EngineeringExecutionContext",
    "EngineeringExecutionAgentInput",
    "EngineeringExecutionAgentOutput",
    "ExecutionStatusLiteral",
    "ToolTypeLiteral",
    "OperationTypeLiteral",
    "exec_config",
]
