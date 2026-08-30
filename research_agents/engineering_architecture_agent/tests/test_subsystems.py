"""
Unit tests for SubsystemDecomposer and ComponentRoleMapper.
"""

from research_agents.engineering_architecture_agent.schemas import ProjectMeta
from research_agents.engineering_architecture_agent.services.role_mapper import ComponentRoleMapper
from research_agents.engineering_architecture_agent.services.subsystem_decomposer import SubsystemDecomposer


def test_subsystem_decomposition_and_role_mapping():
    decomposer = SubsystemDecomposer()
    role_mapper = ComponentRoleMapper()

    project = ProjectMeta(
        title="SAR Drone",
        engineering_domain="Robotics / Edge AI",
        requirements=[
            "Thermal human detection on edge hardware",
            "Real-time edge inference latency under 100ms",
            "Battery-powered operation >= 30 minutes",
            "Autonomous navigation in GPS-denied areas",
        ],
        components=["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5", "ESP32-S3"],
    )

    subsystems = decomposer.decompose(
        project=project,
        decisions=[{"decision_id": "DEC-001", "selected_option": "NVIDIA Jetson Orin Nano 8GB"}],
        requirements=project.requirements,
    )

    assert len(subsystems) >= 4
    sub_names = {s.name for s in subsystems}
    assert "Compute Subsystem" in sub_names
    assert "Sensing Subsystem" in sub_names
    assert "Power Subsystem" in sub_names
    assert "Control Subsystem" in sub_names

    # Check component role mapping
    roles = role_mapper.map_roles(
        subsystems=subsystems,
        decisions=[{"decision_id": "DEC-001", "selected_option": "NVIDIA Jetson Orin Nano 8GB"}],
        project_components=project.components,
    )

    assert len(roles) >= 3
    jetson_role = next(r for r in roles if "Jetson" in r.component)
    assert jetson_role.status == "mandatory"
    assert jetson_role.role == "primary_processor"
    assert "DEC-001" in jetson_role.supporting_decision_ids
