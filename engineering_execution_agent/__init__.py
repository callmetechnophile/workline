"""
Root alias module proxying to research_agents.engineering_execution_agent.
Allows direct execution via `python -m engineering_execution_agent`.
"""

from research_agents.engineering_execution_agent import (
    ArmorIQClient,
    AuthorizedExecution,
    DelegationObject,
    EngineeringExecutionContext,
    EngineeringExecutionAgent,
    EngineeringExecutionAgentInput,
    EngineeringExecutionAgentOutput,
    ExecutionAuditItem,
    ExecutionGraph,
    ExecutionReceipt,
    ExecutionStatusLiteral,
    ExecutionTask,
    MockArmorIQClient,
    OperationTypeLiteral,
    ToolCallRecord,
    ToolTypeLiteral,
    exec_config,
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
