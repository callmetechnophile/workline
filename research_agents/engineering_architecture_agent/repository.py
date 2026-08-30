"""
Repository interface for EngineeringArchitectureAgent subsystems, interfaces, power domains, and graphs.
Defines abstract persistence methods for future SurrealDB integration with in-memory test fallback (Section 41).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureDecision,
    ArchitectureRisk,
    ArchitectureValidationRequirement,
    ComponentRoleItem,
    ControlFlowItem,
    DataFlowItem,
    DependencyItem,
    EngineeringArchitectureAgentOutput,
    InterfaceItem,
    PowerDomainItem,
    SubsystemItem,
)


class ArchitectureRepository(ABC):
    """Abstract persistence interface for system architectures, subsystems, interfaces, and graphs."""

    @abstractmethod
    async def save_architecture(self, output: EngineeringArchitectureAgentOutput) -> str:
        """Persists full architecture model."""
        pass

    @abstractmethod
    async def save_subsystem(self, subsystem: SubsystemItem, project_id: str) -> str:
        """Persists subsystem definition."""
        pass

    @abstractmethod
    async def save_component_role(self, role: ComponentRoleItem, project_id: str) -> str:
        """Persists component role mapping."""
        pass

    @abstractmethod
    async def save_interface(self, iface: InterfaceItem, project_id: str) -> str:
        """Persists interface specification."""
        pass

    @abstractmethod
    async def save_power_domain(self, power: PowerDomainItem, project_id: str) -> str:
        """Persists power domain."""
        pass

    @abstractmethod
    async def save_data_flow(self, flow: DataFlowItem, project_id: str) -> str:
        """Persists data flow."""
        pass

    @abstractmethod
    async def save_control_flow(self, flow: ControlFlowItem, project_id: str) -> str:
        """Persists control flow."""
        pass

    @abstractmethod
    async def save_dependency(self, dep: DependencyItem, project_id: str) -> str:
        """Persists dependency relation."""
        pass

    @abstractmethod
    async def save_architecture_decision(self, dec: ArchitectureDecision, project_id: str) -> str:
        """Persists architecture decision."""
        pass

    @abstractmethod
    async def save_architecture_risk(self, risk: ArchitectureRisk, project_id: str) -> str:
        """Persists architecture risk."""
        pass

    @abstractmethod
    async def save_validation_requirement(self, val: ArchitectureValidationRequirement, project_id: str) -> str:
        """Persists architecture validation requirement."""
        pass

    @abstractmethod
    async def save_architecture_relationship(self, source_id: str, target_id: str, rel_type: str) -> str:
        """Persists graph edge relationship."""
        pass

    @abstractmethod
    async def get_architecture(self, project_id: str) -> Optional[EngineeringArchitectureAgentOutput]:
        """Retrieves system architecture by project ID."""
        pass


class InMemoryArchitectureRepository(ArchitectureRepository):
    """In-memory repository used for local development and test suites."""

    def __init__(self):
        self._architectures: Dict[str, EngineeringArchitectureAgentOutput] = {}
        self._subsystems: Dict[str, List[SubsystemItem]] = {}
        self._interfaces: Dict[str, List[InterfaceItem]] = {}
        self._power_domains: Dict[str, List[PowerDomainItem]] = {}
        self._relationships: List[Dict[str, str]] = []

    async def save_architecture(self, output: EngineeringArchitectureAgentOutput) -> str:
        proj_id = output.project.project_id or output.project.title
        self._architectures[proj_id] = output
        return proj_id

    async def save_subsystem(self, subsystem: SubsystemItem, project_id: str) -> str:
        if project_id not in self._subsystems:
            self._subsystems[project_id] = []
        self._subsystems[project_id].append(subsystem)
        return f"{project_id}_{subsystem.subsystem_id}"

    async def save_component_role(self, role: ComponentRoleItem, project_id: str) -> str:
        return f"{project_id}_{role.component}"

    async def save_interface(self, iface: InterfaceItem, project_id: str) -> str:
        if project_id not in self._interfaces:
            self._interfaces[project_id] = []
        self._interfaces[project_id].append(iface)
        return f"{project_id}_{iface.interface_id}"

    async def save_power_domain(self, power: PowerDomainItem, project_id: str) -> str:
        if project_id not in self._power_domains:
            self._power_domains[project_id] = []
        self._power_domains[project_id].append(power)
        return f"{project_id}_{power.power_domain_id}"

    async def save_data_flow(self, flow: DataFlowItem, project_id: str) -> str:
        return f"{project_id}_{flow.flow_id}"

    async def save_control_flow(self, flow: ControlFlowItem, project_id: str) -> str:
        return f"{project_id}_{flow.control_id}"

    async def save_dependency(self, dep: DependencyItem, project_id: str) -> str:
        return f"{project_id}_{dep.dependency_id}"

    async def save_architecture_decision(self, dec: ArchitectureDecision, project_id: str) -> str:
        return f"{project_id}_{dec.architecture_decision_id}"

    async def save_architecture_risk(self, risk: ArchitectureRisk, project_id: str) -> str:
        return f"{project_id}_{risk.risk_id}"

    async def save_validation_requirement(self, val: ArchitectureValidationRequirement, project_id: str) -> str:
        return f"{project_id}_{val.validation_id}"

    async def save_architecture_relationship(self, source_id: str, target_id: str, rel_type: str) -> str:
        self._relationships.append({"source": source_id, "target": target_id, "relationship": rel_type})
        return f"{source_id}->{rel_type}->{target_id}"

    async def get_architecture(self, project_id: str) -> Optional[EngineeringArchitectureAgentOutput]:
        return self._architectures.get(project_id)
