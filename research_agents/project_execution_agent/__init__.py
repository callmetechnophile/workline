"""
ProjectExecutionAgent package (Agent #10).
Generates Work Breakdown Structures (WBS), Task Dependency DAGs,
and ArmorIQ-scoped Implementation Plans from validated engineering designs.
"""

from research_agents.project_execution_agent.agent import ProjectExecutionAgent
from research_agents.project_execution_agent.schemas import (
    DependencyDAG,
    ImplementationPlan,
    PlanningTask,
    ProjectExecutionAgentInput,
    ProjectExecutionAgentOutput,
    WorkPackage,
)

__all__ = [
    "ProjectExecutionAgent",
    "ProjectExecutionAgentInput",
    "ProjectExecutionAgentOutput",
    "WorkPackage",
    "PlanningTask",
    "ImplementationPlan",
    "DependencyDAG",
]
