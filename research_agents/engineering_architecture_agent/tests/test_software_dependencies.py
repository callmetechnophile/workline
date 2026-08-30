"""
Unit tests for SoftwareArchitect and DependencyAnalyzer.
"""

from research_agents.engineering_architecture_agent.schemas import ProjectMeta, SubsystemItem
from research_agents.engineering_architecture_agent.services.dependency_analyzer import DependencyAnalyzer
from research_agents.engineering_architecture_agent.services.software_architect import SoftwareArchitect


def test_software_stack_and_dependencies():
    sw_architect = SoftwareArchitect()
    dep_analyzer = DependencyAnalyzer()

    subsystems = [
        SubsystemItem(subsystem_id="SUB-001", name="Compute Subsystem", purpose="AI compute"),
        SubsystemItem(subsystem_id="SUB-002", name="Sensing Subsystem", purpose="Sensors"),
        SubsystemItem(subsystem_id="SUB-003", name="Power Subsystem", purpose="Power"),
    ]

    # Software Stack
    layers, boundary = sw_architect.design_software_stack(subsystems)
    assert len(layers) >= 4
    layer_names = {l.name for l in layers}
    assert any("Drivers" in n or "Hardware Abstraction" in n for n in layer_names)
    assert any("AI Inference" in n for n in layer_names)
    assert any("Middleware" in n for n in layer_names)

    # HW/SW Boundary
    assert len(boundary.hardware_responsibilities) > 0
    assert len(boundary.firmware_responsibilities) > 0
    assert len(boundary.software_responsibilities) > 0
    assert len(boundary.ai_responsibilities) > 0

    # Dependencies & Architecture Decisions
    deps, decisions, alternatives, risks, validations = dep_analyzer.analyze(
        ProjectMeta(title="SAR Drone"), subsystems, []
    )

    assert len(deps) >= 2
    assert any(d.dependency_type == "power" for d in deps)
    assert any(d.dependency_type == "communication" for d in deps)

    assert len(decisions) >= 1
    assert len(alternatives) >= 1
    assert len(risks) >= 1
    assert len(validations) >= 1
