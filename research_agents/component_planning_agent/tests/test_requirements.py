"""
Unit tests for ComponentRequirementGenerator (Section 7).
"""

from research_agents.component_planning_agent.schemas import ProjectMeta
from research_agents.component_planning_agent.services.requirement_generator import ComponentRequirementGenerator


def test_component_requirement_generation_and_categories():
    generator = ComponentRequirementGenerator()
    project = ProjectMeta(
        title="SAR Drone",
        engineering_domain="Robotics / Edge AI",
        requirements=["Thermal human detection", "Real-time AI compute"],
    )

    subsystems = [
        {"subsystem_id": "SUB-001", "name": "Compute Subsystem"},
        {"subsystem_id": "SUB-002", "name": "Sensing Subsystem"},
    ]

    reqs = generator.generate_requirements(
        project=project,
        subsystems=subsystems,
        component_roles=[],
        power_domains=[],
        engineering_decisions=[{"decision_id": "DEC-001"}],
    )

    assert len(reqs) >= 4
    categories = {r.category for r in reqs}
    assert "SBC" in categories
    assert "thermal camera" in categories
    assert "microcontroller" in categories
    assert "DC-DC converter" in categories

    sbc_req = next(r for r in reqs if r.category == "SBC")
    assert sbc_req.required_specifications["ai_compute"] == ">= 40 TOPS"
    assert sbc_req.source_subsystem == "SUB-001"
