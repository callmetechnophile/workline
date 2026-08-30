"""
CLI entry point for EngineeringArchitectureAgent (Agent #6) development mode (Section 44).
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

from research_agents.engineering_architecture_agent.agent import EngineeringArchitectureAgent
from research_agents.engineering_architecture_agent.providers.mock_provider import MockEngineeringArchitectureProvider
from research_agents.engineering_architecture_agent.schemas import (
    EngineeringArchitectureAgentInput,
    ProjectMeta,
)


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringArchitectureAgent (Agent #6) CLI Development Mode"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Optional path to engineering synthesis JSON input file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Optional directory to export the 8 architecture artifacts",
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
        help="Run offline demo with complete synthetic SAR drone architecture bundle",
    )

    parsed = parser.parse_args(args)

    # Build input data
    if parsed.input and Path(parsed.input).exists():
        raw_json = json.loads(Path(parsed.input).read_text(encoding="utf-8"))
        input_data = EngineeringArchitectureAgentInput.model_validate(raw_json)
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
                "Low deployment latency (< 5 minutes setup)",
                "Battery-powered operation >= 30 minutes",
                "Long-range wireless telemetry downlink",
            ],
            constraints=["payload power <= 20 W", "payload weight <= 500g"],
            components=["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5", "ESP32-S3"],
            technologies=["TensorRT 8.6", "ROS 2 Humble", "PX4 Autopilot"],
        )

        decisions_fixture = [
            {
                "decision_id": "DEC-001",
                "decision_area": "Primary Edge AI Compute",
                "selected_option": "NVIDIA Jetson Orin Nano 8GB",
                "decision_reason": "Delivers 40 TOPS AI compute for 45 FPS thermal detection at 15 W.",
            }
        ]

        input_data = EngineeringArchitectureAgentInput(
            project=project_meta,
            decisions=decisions_fixture,
            output_dir=parsed.output,
        )

    # In demo mode, use MockEngineeringArchitectureProvider
    agent = EngineeringArchitectureAgent(reasoning_provider=MockEngineeringArchitectureProvider())
    output = agent.run_sync(input_data)

    # CLI Output matching Section 44 format
    print(f"\nProject:\n{output.project.title}\n")
    print(f"Architecture:\n{output.architecture.architecture_name}\n")
    print(f"Subsystems:\n{len(output.subsystems)}\n")
    print(f"Interfaces:\n{len(output.interfaces)}\n")
    print(f"Power Domains:\n{len(output.power_domains)}\n")
    print(f"Data Flows:\n{len(output.data_flows)}\n")
    print(f"Control Flows:\n{len(output.control_flows)}\n")
    print(f"Dependencies:\n{len(output.dependencies)}\n")
    print(f"Architecture Risks:\n{len(output.risks)}\n")
    print(f"Validation Requirements:\n{len(output.validation_requirements)}\n")
    print("+ Architecture generated")
    print("+ Traceability generated")
    print("+ Block diagram generated")
    print("+ Architecture graph generated\n")


if __name__ == "__main__":
    main()
