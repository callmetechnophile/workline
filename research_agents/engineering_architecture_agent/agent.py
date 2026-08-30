"""
Agent #6: EngineeringArchitectureAgent implementation using Google ADK conventions.
Transforms engineering decisions, requirements, and findings into a concrete system architecture.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from research_agents.engineering_architecture_agent.providers.base import (
    ProviderError,
    ReasoningProvider,
)
from research_agents.engineering_architecture_agent.providers.bedrock import BedrockProvider
from research_agents.engineering_architecture_agent.schemas import (
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
from research_agents.engineering_architecture_agent.services.dependency_analyzer import DependencyAnalyzer
from research_agents.engineering_architecture_agent.services.file_exporter import ArchitectureFileExporter
from research_agents.engineering_architecture_agent.services.flow_builder import FlowBuilder
from research_agents.engineering_architecture_agent.services.graph_builder import GraphBuilder
from research_agents.engineering_architecture_agent.services.interface_designer import InterfaceDesigner
from research_agents.engineering_architecture_agent.services.power_architect import PowerArchitect
from research_agents.engineering_architecture_agent.services.report_generator import ArchitectureReportGenerator
from research_agents.engineering_architecture_agent.services.role_mapper import ComponentRoleMapper
from research_agents.engineering_architecture_agent.services.software_architect import SoftwareArchitect
from research_agents.engineering_architecture_agent.services.subsystem_decomposer import SubsystemDecomposer


class EngineeringArchitectureAgent:
    """
    Google ADK-compliant Engineering Architecture & System Design Agent.
    Transforms engineering decisions and requirements into a traceable system architecture
    containing subsystems, interfaces, power domains, data flows, dependencies, and validation requirements.
    """

    NAME = "EngineeringArchitectureAgent"
    DESCRIPTION = (
        "Transforms engineering decisions and requirements into a traceable system architecture "
        "containing subsystems, interfaces, power domains, data flows, dependencies, and validation requirements."
    )
    CAPABILITIES = [
        "architecture.build",
        "architecture.decompose",
        "architecture.interfaces",
        "architecture.power",
        "architecture.dataflow",
        "architecture.dependencies",
        "architecture.validate",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        subsystem_decomposer: Optional[SubsystemDecomposer] = None,
        role_mapper: Optional[ComponentRoleMapper] = None,
        interface_designer: Optional[InterfaceDesigner] = None,
        power_architect: Optional[PowerArchitect] = None,
        flow_builder: Optional[FlowBuilder] = None,
        software_architect: Optional[SoftwareArchitect] = None,
        dependency_analyzer: Optional[DependencyAnalyzer] = None,
        graph_builder: Optional[GraphBuilder] = None,
        report_generator: Optional[ArchitectureReportGenerator] = None,
        file_exporter: Optional[ArchitectureFileExporter] = None,
    ):
        self.provider = reasoning_provider or BedrockProvider()
        self.subsystem_decomposer = subsystem_decomposer or SubsystemDecomposer()
        self.role_mapper = role_mapper or ComponentRoleMapper()
        self.interface_designer = interface_designer or InterfaceDesigner()
        self.power_architect = power_architect or PowerArchitect()
        self.flow_builder = flow_builder or FlowBuilder()
        self.software_architect = software_architect or SoftwareArchitect()
        self.dependency_analyzer = dependency_analyzer or DependencyAnalyzer()
        self.graph_builder = graph_builder or GraphBuilder()
        self.report_generator = report_generator or ArchitectureReportGenerator()
        self.file_exporter = file_exporter or ArchitectureFileExporter()

    async def run(
        self,
        input_data: EngineeringArchitectureAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringArchitectureAgentOutput:
        """
        Executes end-to-end system architecture decomposition and generation.
        """
        start_time = time.time()
        exec_id = (
            execution_id
            or (input_data.execution_context.execution_id if input_data.execution_context else None)
            or f"exec_{uuid.uuid4().hex[:8]}"
        )

        logger.info(
            f"[{exec_id}][{self.NAME}] Starting architecture design for project='{input_data.project.title}'"
        )

        # 1. Subsystem Decomposition (Section 6 & 7)
        subsystems = self.subsystem_decomposer.decompose(
            project=input_data.project,
            decisions=input_data.decisions,
            requirements=input_data.project.requirements or input_data.project.objectives,
        )

        # 2. Component Role Mapping (Section 8 & 9)
        component_roles = self.role_mapper.map_roles(
            subsystems=subsystems,
            decisions=input_data.decisions,
            project_components=input_data.project.components,
        )

        # 3. Interface Design (Section 10, 11, 12)
        interfaces = self.interface_designer.design_interfaces(subsystems=subsystems)

        # 4. Power Architecture (Section 13 & 14)
        power_domains = self.power_architect.build_power_domains(subsystems=subsystems)

        # 5. Data Flow, Control Flow & Feedback Loops (Sections 15, 16, 17, 18)
        data_flows, control_flows, feedback_loops = self.flow_builder.build_flows(subsystems=subsystems)

        # 6. Software Architecture & HW/SW Boundary (Sections 19 & 20)
        software_layers, hw_sw_boundary = self.software_architect.design_software_stack(subsystems=subsystems)

        # 7. Dependencies, Decisions, Alternatives, Risks & Validation (Sections 24-29)
        dependencies, arch_decisions, alternatives, risks, validations = self.dependency_analyzer.analyze(
            project=input_data.project,
            subsystems=subsystems,
            decisions=input_data.decisions,
        )

        # 8. Block Diagram, Architecture Graph & Traceability (Sections 30, 31, 32)
        block_diagram, architecture_graph, traceability = self.graph_builder.build_diagram_and_graph(
            project=input_data.project,
            subsystems=subsystems,
            component_roles=component_roles,
            interfaces=interfaces,
            power_domains=power_domains,
            arch_decisions=arch_decisions,
            validations=validations,
        )

        # Component requirements for downstream Agent #7 (Section 35)
        comp_reqs: List[ArchitectureComponentRequirement] = [
            ArchitectureComponentRequirement(
                category="Edge AI Compute Module",
                quantity=1,
                required_specs=["NVIDIA Ampere architecture", ">= 40 TOPS AI compute", "8GB RAM"],
                reason="Primary host for real-time vision model.",
                source_subsystem="SUB-001",
            ),
            ArchitectureComponentRequirement(
                category="Thermal LWIR Sensor",
                quantity=1,
                required_specs=["160x120 radiometric LWIR", "SPI VoSPI video", "3.3V logic"],
                reason="Thermal target detection sensor.",
                source_subsystem="SUB-002",
            ),
        ]

        architecture_meta = ArchitectureMeta(
            architecture_id="ARCH-001",
            architecture_name=f"{input_data.project.title} System Architecture",
            description=f"Heterogeneous multi-domain system architecture for {input_data.project.title}.",
            architecture_type="Heterogeneous Edge-Compute / Real-time Controller",
            confidence=0.92,
        )

        # 9. 20-Section Markdown Architecture Report (Section 46)
        report_markdown = self.report_generator.generate_report(
            project=input_data.project,
            architecture=architecture_meta,
            subsystems=subsystems,
            component_roles=component_roles,
            interfaces=interfaces,
            power_domains=power_domains,
            data_flows=data_flows,
            control_flows=control_flows,
            software_architecture=software_layers,
            hw_sw_boundary=hw_sw_boundary,
            physical_architecture=[],
            thermal_architecture=[],
            communication_architecture=interfaces,
            dependencies=dependencies,
            arch_decisions=arch_decisions,
            alternatives=alternatives,
            risks=risks,
            validations=validations,
            traceability=traceability,
            assumptions=[],
            unknowns=[],
        )

        output = EngineeringArchitectureAgentOutput(
            status="success",
            project=input_data.project,
            architecture=architecture_meta,
            subsystems=subsystems,
            component_roles=component_roles,
            interfaces=interfaces,
            power_domains=power_domains,
            data_flows=data_flows,
            control_flows=control_flows,
            feedback_loops=feedback_loops,
            software_architecture=software_layers,
            hardware_software_boundary=hw_sw_boundary,
            physical_architecture=[],
            thermal_architecture=[],
            communication_architecture=interfaces,
            dependencies=dependencies,
            architecture_decisions=arch_decisions,
            alternatives=alternatives,
            risks=risks,
            validation_requirements=validations,
            traceability=traceability,
            block_diagram=block_diagram,
            architecture_graph=architecture_graph,
            component_requirements=comp_reqs,
            structured_report_markdown=report_markdown,
        )

        # 10. File Export if output_dir provided (Section 45)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{exec_id}][{self.NAME}] Architecture built in {elapsed:.3f}s: "
            f"Subsystems={len(subsystems)} Interfaces={len(interfaces)} "
            f"PowerDomains={len(power_domains)} DataFlows={len(data_flows)} Dependencies={len(dependencies)}"
        )

        return output

    def run_sync(
        self,
        input_data: EngineeringArchitectureAgentInput,
        execution_id: Optional[str] = None,
    ) -> EngineeringArchitectureAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods
    # =========================================================================

    def build_architecture(self, input_data: EngineeringArchitectureAgentInput) -> EngineeringArchitectureAgentOutput:
        """ADK Capability: Builds complete system architecture synchronously."""
        return self.run_sync(input_data)

    def decompose_subsystems(self, project: ProjectMeta, reqs: List[str]) -> List[SubsystemItem]:
        """ADK Capability: Decomposes project into logical subsystems."""
        return self.subsystem_decomposer.decompose(project, [], reqs)

    def map_component_roles(self, subsystems: List[SubsystemItem], components: List[str]) -> List[ComponentRoleItem]:
        """ADK Capability: Maps components into subsystem roles."""
        return self.role_mapper.map_roles(subsystems, [], components)

    def define_interfaces(self, subsystems: List[SubsystemItem]) -> List[InterfaceItem]:
        """ADK Capability: Designs inter-subsystem electrical & communication interfaces."""
        return self.interface_designer.design_interfaces(subsystems)

    def build_power_architecture(self, subsystems: List[SubsystemItem]) -> List[PowerDomainItem]:
        """ADK Capability: Constructs power domains and voltage rails."""
        return self.power_architect.build_power_domains(subsystems)

    def build_data_flows(self, subsystems: List[SubsystemItem]) -> List[DataFlowItem]:
        """ADK Capability: Synthesizes data flows across subsystems."""
        flows, _, _ = self.flow_builder.build_flows(subsystems)
        return flows

    def build_control_flows(self, subsystems: List[SubsystemItem]) -> List[ControlFlowItem]:
        """ADK Capability: Synthesizes control triggers and decision stages."""
        _, flows, _ = self.flow_builder.build_flows(subsystems)
        return flows

    def build_software_architecture(self, subsystems: List[SubsystemItem]) -> List[SoftwareLayerItem]:
        """ADK Capability: Outlines layered software architecture stack."""
        layers, _ = self.software_architect.design_software_stack(subsystems)
        return layers

    def build_dependency_graph(self, project: ProjectMeta, subsystems: List[SubsystemItem]) -> List[DependencyItem]:
        """ADK Capability: Resolves inter-subsystem dependencies."""
        deps, _, _, _, _ = self.dependency_analyzer.analyze(project, subsystems, [])
        return deps

    def analyze_architecture_risks(self, project: ProjectMeta, subsystems: List[SubsystemItem]) -> List[ArchitectureRisk]:
        """ADK Capability: Evaluates architecture-level technical risks."""
        _, _, _, risks, _ = self.dependency_analyzer.analyze(project, subsystems, [])
        return risks

    def generate_validation_requirements(
        self, project: ProjectMeta, subsystems: List[SubsystemItem]
    ) -> List[ArchitectureValidationRequirement]:
        """ADK Capability: Formulates architecture validation requirements."""
        _, _, _, _, validations = self.dependency_analyzer.analyze(project, subsystems, [])
        return validations

    def generate_traceability(
        self, project: ProjectMeta, subsystems: List[SubsystemItem]
    ) -> List[ArchitectureTraceability]:
        """ADK Capability: Generates requirement-to-validation traceability."""
        _, _, trace = self.graph_builder.build_diagram_and_graph(
            project, subsystems, [], [], [], [], []
        )
        return trace
