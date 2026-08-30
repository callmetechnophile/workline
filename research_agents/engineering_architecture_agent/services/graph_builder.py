"""
Block diagram and architecture graph construction service for EngineeringArchitectureAgent (Sections 30, 31, 32).
"""

from typing import List, Tuple
from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureDecision,
    ArchitectureGraph,
    ArchitectureTraceability,
    ArchitectureValidationRequirement,
    BlockDiagram,
    ComponentRoleItem,
    DiagramEdge,
    DiagramNode,
    GraphEdge,
    GraphNode,
    InterfaceItem,
    PowerDomainItem,
    ProjectMeta,
    SubsystemItem,
)


class GraphBuilder:
    """Constructs machine-readable block diagrams, typed architecture graphs, and traceability chains."""

    def build_diagram_and_graph(
        self,
        project: ProjectMeta,
        subsystems: List[SubsystemItem],
        component_roles: List[ComponentRoleItem],
        interfaces: List[InterfaceItem],
        power_domains: List[PowerDomainItem],
        arch_decisions: List[ArchitectureDecision],
        validations: List[ArchitectureValidationRequirement],
    ) -> Tuple[BlockDiagram, ArchitectureGraph, List[ArchitectureTraceability]]:
        """
        Synthesizes block diagram, architecture graph, and requirement-to-validation traceability.
        """
        # 1. Block Diagram (Section 31)
        diag_nodes: List[DiagramNode] = []
        diag_edges: List[DiagramEdge] = []

        for sub in subsystems:
            diag_nodes.append(
                DiagramNode(
                    id=sub.subsystem_id,
                    type="subsystem",
                    label=sub.name,
                    subsystem=sub.subsystem_id,
                )
            )

        for iface in interfaces:
            diag_edges.append(
                DiagramEdge(
                    source=iface.source,
                    target=iface.target,
                    type="data" if iface.interface_type in ("SPI", "UART", "I2C", "CSI") else "control",
                    label=f"{iface.interface_type} ({iface.voltage_logic or ''})",
                )
            )

        block_diagram = BlockDiagram(nodes=diag_nodes, edges=diag_edges)

        # 2. Typed Architecture Graph (Section 32)
        graph_nodes: List[GraphNode] = []
        graph_edges: List[GraphEdge] = []

        # Project root node
        proj_id = project.project_id or "proj_root"
        graph_nodes.append(GraphNode(id=proj_id, type="project", label=project.title))

        # Subsystems & Component Nodes
        for sub in subsystems:
            graph_nodes.append(GraphNode(id=sub.subsystem_id, type="subsystem", label=sub.name))
            graph_edges.append(GraphEdge(source=proj_id, target=sub.subsystem_id, relationship="contains"))

        for role in component_roles:
            comp_node_id = f"comp_{role.component.lower().replace(' ', '_')}"
            graph_nodes.append(GraphNode(id=comp_node_id, type="component", label=role.component, properties={"role": role.role, "status": role.status}))
            graph_edges.append(GraphEdge(source=role.subsystem_id, target=comp_node_id, relationship="contains"))

        # Interface Nodes
        for iface in interfaces:
            graph_nodes.append(GraphNode(id=iface.interface_id, type="interface", label=f"{iface.interface_type} Bus"))
            graph_edges.append(GraphEdge(source=iface.source, target=iface.interface_id, relationship="connects_to"))
            graph_edges.append(GraphEdge(source=iface.interface_id, target=iface.target, relationship="connects_to"))

        # Power Domains
        for pwr in power_domains:
            graph_nodes.append(GraphNode(id=pwr.power_domain_id, type="power_domain", label=pwr.name, properties={"voltage": pwr.voltage}))
            graph_edges.append(GraphEdge(source=proj_id, target=pwr.power_domain_id, relationship="powered_by"))

        architecture_graph = ArchitectureGraph(nodes=graph_nodes, edges=graph_edges)

        # 3. Architecture Traceability (Section 30)
        traceability: List[ArchitectureTraceability] = []
        req_ids = [f"REQ-{i:03d}" for i in range(1, len(project.requirements) + 1)] if project.requirements else ["REQ-001"]
        eng_dec_ids = ["DEC-001"]

        traceability.append(
            ArchitectureTraceability(
                traceability_id="TRACE-ARCH-001",
                requirement_ids=req_ids[:2],
                engineering_decision_ids=eng_dec_ids,
                architecture_decision_ids=[d.architecture_decision_id for d in arch_decisions],
                subsystem_ids=[s.subsystem_id for s in subsystems],
                component_ids=[r.component for r in component_roles],
                interface_ids=[i.interface_id for i in interfaces],
                validation_ids=[v.validation_id for v in validations],
            )
        )

        return block_diagram, architecture_graph, traceability
