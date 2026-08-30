"""
CLI entry point for EngineeringSynthesisAgent (Agent #5) development mode (Section 35).
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

from research_agents.engineering_synthesis_agent.agent import EngineeringSynthesisAgent
from research_agents.engineering_synthesis_agent.providers.mock_provider import MockEngineeringSynthesisProvider
from research_agents.engineering_synthesis_agent.schemas import (
    EngineeringSynthesisAgentInput,
    ProjectMeta,
)


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringSynthesisAgent (Agent #5) CLI Development Mode"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=str,
        default=None,
        help="Optional path to research bundle JSON input file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Optional directory to export the 5 engineering artifacts",
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
        help="Run offline demo with complete synthetic multi-agent research bundle",
    )

    parsed = parser.parse_args(args)

    # Build input data
    if parsed.input and Path(parsed.input).exists():
        raw_json = json.loads(Path(parsed.input).read_text(encoding="utf-8"))
        input_data = EngineeringSynthesisAgentInput.model_validate(raw_json)
    else:
        # Default SAR Drone demo context
        project_meta = ProjectMeta(
            project_id="proj_sar_drone_001",
            title=parsed.project,
            description="Autonomous UAV for human detection in disaster search zones.",
            engineering_domain="Robotics / Edge AI / UAV",
            requirements=[
                "Thermal human detection on edge hardware",
                "Real-time edge inference latency under 100ms",
                "Autonomous navigation in GPS-denied areas",
                "Low deployment latency (< 5 minutes setup)",
                "Battery-powered operation >= 30 minutes",
            ],
            constraints=["payload power <= 20 W", "payload weight <= 500g"],
            components=["NVIDIA Jetson Orin Nano", "FLIR Lepton 3.5", "ESP32-S3"],
            technologies=["YOLOv8n", "TensorRT", "ROS 2 Humble"],
        )

        sample_papers = [
            {"paper_id": "ev_p_001", "title": "Thermal Drone Vision", "abstract": "Achieved 45 FPS on Jetson Orin Nano at 15 W."}
        ]
        sample_web = [
            {"source_id": "ev_w_001", "title": "Jetson Specs", "description": "40 TOPS AI compute at 15 W.", "source_type": "manufacturer_documentation"}
        ]
        sample_facts = [
            {"fact": "FLIR Lepton 3.5 operates at 3.3 V with SPI video.", "source_document": "ev_f_001", "page": 4}
        ]
        deep_research_fixture = {
            "extracted_claims": [
                {"claim": "NVIDIA Jetson Orin Nano delivers up to 40 TOPS AI compute at 15 W.", "source_evidence_ids": ["ev_w_001"], "confidence": 0.98},
                {"claim": "FLIR Lepton 3.5 radiometric sensor provides 8.7 Hz refresh rate.", "source_evidence_ids": ["ev_f_001"], "confidence": 0.96},
            ],
            "component_trade_studies": [
                {
                    "component_type": "Edge Compute Platform",
                    "candidates_evaluated": ["NVIDIA Jetson Orin Nano", "Raspberry Pi 5", "ESP32-S3"],
                    "tradeoff_matrix": {
                        "NVIDIA Jetson Orin Nano": {"AI_TOPS": 40, "Power_W": 15},
                        "Raspberry Pi 5": {"AI_TOPS": 0, "Power_W": 12},
                    },
                    "recommended_option": "NVIDIA Jetson Orin Nano",
                    "recommendation_reason": "Satisfies 30+ FPS latency requirement with 40 TOPS INT8 TensorRT support.",
                }
            ],
            "engineering_implications": [
                {"category": "power", "finding": "15 W compute load requires 5V/5A buck regulator.", "impact_on_project": "Prevents brownouts."}
            ],
        }

        input_data = EngineeringSynthesisAgentInput(
            project=project_meta,
            deep_research=deep_research_fixture,
            research_papers=sample_papers,
            web_sources=sample_web,
            facts=sample_facts,
            output_dir=parsed.output,
        )

    agent = EngineeringSynthesisAgent(reasoning_provider=MockEngineeringSynthesisProvider())
    output = agent.run_sync(input_data)

    # CLI Output matching Section 35 format
    print(f"\nProject:\n{output.project.title}\n")
    print(f"Requirements:\n{len(output.requirement_analysis)}\n")
    print(f"Technical Findings:\n{len(output.technical_findings)}\n")
    print(f"Trade-offs:\n{len(output.tradeoffs)}\n")
    print(f"Engineering Decisions:\n{len(output.decisions)}\n")
    print(f"Recommendations:\n{len(output.recommendations)}\n")
    print(f"Risks:\n{len(output.risks)}\n")
    print(f"Unknowns:\n{len(output.unknowns)}\n")
    print(f"Validation Requirements:\n{len(output.validation_requirements)}\n")
    print(f"Overall Confidence:\n{output.overall_confidence:.2f}\n")
    print("+ Evidence traceability generated")
    print("+ Engineering decisions generated")
    print("+ Validation plan generated\n")


if __name__ == "__main__":
    main()
