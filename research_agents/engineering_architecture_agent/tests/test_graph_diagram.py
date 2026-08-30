"""
Unit tests for GraphBuilder (block diagram, architecture graph, and traceability).
"""

from research_agents.engineering_architecture_agent.schemas import (
    ArchitectureDecision,
    ArchitectureValidationRequirement,
    ComponentRoleItem,
    InterfaceItem,
    PowerDomainItem,
    ProjectMeta,
    SubsystemItem,
)
from research_agents.engineering_architecture_agent.services.graph_builder import GraphBuilder


def test_block_diagram_and_architecture_graph():
    builder = GraphBuilder()
    project = ProjectMeta(title="SAR Drone", requirements=["Thermal detection"])

    subsystems = [
        SubsystemItem(subsystem_id="SUB-001", name="Compute Subsystem", purpose="AI compute"),
        SubsystemItem(subsystem_id="SUB-002", name="Sensing Subsystem", purpose="Sensors"),
    ]
    roles = [
        ComponentRoleItem(component="Jetson Orin Nano", role="processor", subsystem_id="SUB-001", reason="AI"),
        ComponentRoleItem(component="FLIR Lepton", role="sensor", subsystem_id="SUB-002", reason="Thermal"),
    ]
    interfaces = [
        InterfaceItem(interface_id="IF-001", source="SUB-002", target="SUB-001", interface_type="SPI", purpose="Video")
    ]
    power_domains = [
        PowerDomainItem(power_domain_id="PWR-001", name="5V Rail", source="Buck", voltage="5.0V", regulation="Buck", protection=[])
    ]
    decisions = [
        ArchitectureDecision(architecture_decision_id="ARCH-DEC-001", decision_area="Compute", selected_architecture="Edge", reason="AI")
    ]
    validations = [
        ArchitectureValidationRequirement(validation_id="VAL-001", category="electrical", description="Test", acceptance_criteria="OK")
    ]

    block_diagram, graph, traceability = builder.build_diagram_and_graph(
        project, subsystems, roles, interfaces, power_domains, decisions, validations
    )

    # Check Block Diagram
    assert len(block_diagram.nodes) == 2
    assert len(block_diagram.edges) == 1
    assert block_diagram.edges[0].source == "SUB-002"

    # Check Architecture Graph
    assert len(graph.nodes) >= 4
    rel_types = {e.relationship for e in graph.edges}
    assert "contains" in rel_types
    assert "connects_to" in rel_types
    assert "powered_by" in rel_types

    # Check Traceability
    assert len(traceability) >= 1
    assert "REQ-001" in traceability[0].requirement_ids
    assert "ARCH-DEC-001" in traceability[0].architecture_decision_ids
    assert "VAL-001" in traceability[0].validation_ids
