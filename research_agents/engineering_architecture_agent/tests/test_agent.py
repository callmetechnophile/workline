"""
End-to-end unit and integration tests for EngineeringArchitectureAgent (Agent #6).
"""

import pytest
from research_agents.engineering_architecture_agent.agent import EngineeringArchitectureAgent
from research_agents.engineering_architecture_agent.providers.mock_provider import MockEngineeringArchitectureProvider
from research_agents.engineering_architecture_agent.schemas import (
    EngineeringArchitectureAgentInput,
    ProjectMeta,
)


@pytest.mark.asyncio
async def test_engineering_architecture_agent_successful_run():
    agent = EngineeringArchitectureAgent(reasoning_provider=MockEngineeringArchitectureProvider())
    input_data = EngineeringArchitectureAgentInput(
        project=ProjectMeta(
            title="Autonomous Search and Rescue Drone",
            engineering_domain="Robotics / Edge AI / UAV",
            requirements=[
                "Thermal human detection on edge hardware",
                "Real-time edge inference latency under 100ms",
                "Battery-powered operation >= 30 minutes",
                "Autonomous navigation in GPS-denied areas",
            ],
            constraints=["payload power <= 20 W"],
            components=["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5", "ESP32-S3"],
        ),
        decisions=[
            {
                "decision_id": "DEC-001",
                "decision_area": "Compute",
                "selected_option": "NVIDIA Jetson Orin Nano 8GB",
                "decision_reason": "40 TOPS AI compute",
            }
        ],
    )

    output = await agent.run(input_data)

    assert output.status == "success"
    assert len(output.subsystems) >= 4
    assert len(output.component_roles) >= 3
    assert len(output.interfaces) >= 3
    assert len(output.power_domains) >= 3
    assert len(output.data_flows) >= 2
    assert len(output.control_flows) >= 1
    assert len(output.feedback_loops) >= 1
    assert len(output.software_architecture) >= 4
    assert output.hardware_software_boundary is not None
    assert len(output.dependencies) >= 3
    assert len(output.architecture_decisions) >= 1
    assert len(output.alternatives) >= 1
    assert len(output.risks) >= 2
    assert len(output.validation_requirements) >= 2
    assert len(output.traceability) >= 1
    assert len(output.block_diagram.nodes) >= 2
    assert len(output.architecture_graph.nodes) >= 4
    assert len(output.component_requirements) >= 2
    assert "# System Architecture" in output.structured_report_markdown


def test_engineering_architecture_agent_sync_execution():
    agent = EngineeringArchitectureAgent(reasoning_provider=MockEngineeringArchitectureProvider())
    input_data = EngineeringArchitectureAgentInput(
        project=ProjectMeta(title="Sync Test SAR Drone", requirements=["Thermal detection"]),
    )

    output = agent.run_sync(input_data)
    assert output.status == "success"
    assert len(output.subsystems) >= 1
