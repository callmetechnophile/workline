"""
CLI entry point for ComponentPlanningAgent (Agent #7) development mode (Section 45).
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

from research_agents.component_planning_agent.agent import ComponentPlanningAgent
from research_agents.component_planning_agent.providers.mock_provider import MockComponentPlanningProvider
from research_agents.component_planning_agent.schemas import (
    ComponentPlanningAgentInput,
    ProjectMeta,
)


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — ComponentPlanningAgent (Agent #7) CLI Development Mode"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Optional path to architecture JSON input file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Optional directory to export the 7 BOM artifacts",
    )
    parser.add_argument(
        "--project",
        "-p",
        type=str,
        default="Autonomous Search and Rescue Drone",
        help="Project title",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run offline demo with complete synthetic SAR drone BOM bundle",
    )

    parsed = parser.parse_args(args)

    # Build input data
    if parsed.input and Path(parsed.input).exists():
        raw_json = json.loads(Path(parsed.input).read_text(encoding="utf-8"))
        input_data = ComponentPlanningAgentInput.model_validate(raw_json)
    else:
        # Default SAR Drone demo context
        project_meta = ProjectMeta(
            project_id="proj_sar_drone_001",
            title=parsed.project,
            description="Autonomous UAV with edge thermal computer vision and real-time autopilot control.",
            engineering_domain="Robotics / Edge AI / UAV",
            requirements=[
                "Thermal human detection on edge hardware",
                "Real-time edge inference latency under 100ms",
                "Autonomous navigation in GPS-denied areas",
                "Battery-powered operation >= 30 minutes",
            ],
            constraints=["payload power <= 20 W", "payload weight <= 500g"],
            components=["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5", "ESP32-S3"],
            technologies=["TensorRT 8.6", "ROS 2 Humble", "ESP-IDF v5.1"],
        )

        input_data = ComponentPlanningAgentInput(
            project=project_meta,
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
            output_dir=parsed.output,
        )

    # In demo mode, use MockComponentPlanningProvider
    agent = ComponentPlanningAgent(reasoning_provider=MockComponentPlanningProvider())
    output = agent.run_sync(input_data)

    # CLI Output matching Section 45 format
    print(f"\nProject:\n{output.project_id}\n")
    print(f"BOM Line Items:\n{output.summary.total_line_items}\n")
    print(f"Selected:\n{output.summary.selected_items}\n")
    print(f"Candidates:\n{output.summary.candidate_items}\n")
    print(f"Pending:\n{output.summary.pending_items}\n")
    print(f"Subsystems:\n{output.summary.subsystem_count}\n")
    print(f"Compatibility Issues:\n{len([c for c in output.compatibility_checks if c.status != 'passed'])}\n")
    print(f"Alternatives:\n{len(output.alternatives)}\n")
    print(f"Validation Requirements:\n{len(output.validation_requirements)}\n")
    print("+ BOM generated")
    print("+ Compatibility checked")
    print("+ Alternatives generated")
    print("+ Traceability generated\n")


if __name__ == "__main__":
    main()
