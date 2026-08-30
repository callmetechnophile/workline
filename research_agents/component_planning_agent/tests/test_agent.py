"""
End-to-end unit and integration tests for ComponentPlanningAgent (Agent #7).
"""

import pytest
from research_agents.component_planning_agent.agent import ComponentPlanningAgent
from research_agents.component_planning_agent.providers.mock_provider import MockComponentPlanningProvider
from research_agents.component_planning_agent.schemas import (
    ComponentPlanningAgentInput,
    ProjectMeta,
)


@pytest.mark.asyncio
async def test_component_planning_agent_successful_run():
    agent = ComponentPlanningAgent(reasoning_provider=MockComponentPlanningProvider())
    input_data = ComponentPlanningAgentInput(
        project=ProjectMeta(
            title="Autonomous Search and Rescue Drone",
            engineering_domain="Robotics / Edge AI / UAV",
            requirements=[
                "Thermal human detection on edge hardware",
                "Real-time edge inference latency under 100ms",
                "Battery-powered operation >= 30 minutes",
            ],
            constraints=["payload power <= 20 W"],
            components=["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5", "ESP32-S3"],
        ),
        subsystems=[
            {"subsystem_id": "SUB-001", "name": "Compute Subsystem"},
            {"subsystem_id": "SUB-002", "name": "Sensing Subsystem"},
            {"subsystem_id": "SUB-003", "name": "Power Subsystem"},
            {"subsystem_id": "SUB-004", "name": "Control Subsystem"},
        ],
        component_roles=[
            {"component": "NVIDIA Jetson Orin Nano 8GB", "role": "primary_edge_compute", "subsystem_id": "SUB-001"},
            {"component": "FLIR Lepton 3.5", "role": "radiometric_thermal_sensor", "subsystem_id": "SUB-002"},
            {"component": "ESP32-S3", "role": "flight_safety_controller", "subsystem_id": "SUB-004"},
        ],
        interfaces=[
            {"interface_id": "IF-001", "source": "SUB-002", "target": "SUB-001", "interface_type": "SPI", "voltage_logic": "3.3V"},
            {"interface_id": "IF-002", "source": "SUB-001", "target": "SUB-004", "interface_type": "UART", "voltage_logic": "3.3V"},
        ],
        power_domains=[
            {"power_domain_id": "PWR-001", "name": "14.8V Battery Main Bus", "voltage": "14.8V"},
            {"power_domain_id": "PWR-002", "name": "5.0V Compute Rail", "voltage": "5.0V"},
            {"power_domain_id": "PWR-003", "name": "3.3V Logic Rail", "voltage": "3.3V"},
        ],
        engineering_decisions=[
            {"decision_id": "DEC-001", "selected_option": "NVIDIA Jetson Orin Nano 8GB", "decision_reason": "40 TOPS AI compute"}
        ],
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert len(output.items) >= 5
    assert output.summary.total_line_items >= 5
    assert output.summary.selected_items >= 4
    assert len(output.component_requirements) >= 4
    assert len(output.compatibility_checks) >= 3
    assert len(output.conflicts) >= 1
    assert len(output.alternatives) >= 2
    assert len(output.validation_requirements) >= 2
    assert len(output.unknowns) >= 1
    assert len(output.assumptions) >= 1
    assert len(output.traceability) >= 1
    assert "# Engineering Bill of Materials" in output.structured_bom_markdown


def test_component_planning_agent_sync_execution():
    agent = ComponentPlanningAgent(reasoning_provider=MockComponentPlanningProvider())
    input_data = ComponentPlanningAgentInput(
        project=ProjectMeta(title="Sync Test SAR Drone", requirements=["Thermal detection"]),
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert len(output.items) >= 1
