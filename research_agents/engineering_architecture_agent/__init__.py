"""
EngineeringArchitectureAgent — Agent #6 of WorkflowGuide AI Platform.
"""

from research_agents.engineering_architecture_agent.agent import EngineeringArchitectureAgent
from research_agents.engineering_architecture_agent.config import arch_config
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureAlternative,
    ArchitectureComponentRequirement,
    ArchitectureDecision,
    ArchitectureGraph,
    ArchitectureMeta,
    ArchitectureRisk,
    ArchitectureTraceability,
    ArchitectureValidationRequirement,
    BlockDiagram,
    ComponentRoleItem,
    ControlFlowItem,
    DataFlowItem,
    DependencyItem,
    EngineeringArchitectureAgentInput,
    EngineeringArchitectureAgentOutput,
    HardwareSoftwareBoundary,
    InterfaceItem,
    PowerDomainItem,
    ProjectMeta,
    SoftwareLayerItem,
    StructuredError,
    SubsystemItem,
)

__all__ = [
    "EngineeringArchitectureAgent",
    "EngineeringArchitectureAgentInput",
    "EngineeringArchitectureAgentOutput",
    "ProjectMeta",
    "ArchitectureMeta",
    "SubsystemItem",
    "ComponentRoleItem",
    "InterfaceItem",
    "PowerDomainItem",
    "DataFlowItem",
    "ControlFlowItem",
    "SoftwareLayerItem",
    "HardwareSoftwareBoundary",
    "DependencyItem",
    "ArchitectureDecision",
    "ArchitectureAlternative",
    "ArchitectureRisk",
    "ArchitectureValidationRequirement",
    "ArchitectureTraceability",
    "BlockDiagram",
    "ArchitectureGraph",
    "ArchitectureComponentRequirement",
    "StructuredError",
    "arch_config",
]
