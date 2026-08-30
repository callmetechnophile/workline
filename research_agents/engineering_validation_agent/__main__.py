"""
CLI entry point for EngineeringValidationAgent (Agent #9) development mode (Section 50).
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List

from research_agents.engineering_validation_agent.agent import EngineeringValidationAgent
from research_agents.engineering_validation_agent.schemas import EngineeringValidationAgentInput


def main(args: List[str] = None):
    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringValidationAgent (Agent #9) CLI Development Mode"
    )
    parser.add_argument(
        "--architecture",
        "-a",
        type=str,
        default=None,
        help="Path to architecture JSON file",
    )
    parser.add_argument(
        "--bom",
        "-b",
        type=str,
        default=None,
        help="Path to BOM JSON file",
    )
    parser.add_argument(
        "--procurement",
        "-p",
        type=str,
        default=None,
        help="Path to procurement optimization JSON file",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Directory to export the 10 validation artifacts",
    )
    parser.add_argument(
        "--project",
        type=str,
        default="Autonomous Search and Rescue Drone",
        help="Project title",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run offline demo with complete synthetic SAR drone validation bundle",
    )

    parsed = parser.parse_args(args)

    arch_dict = {}
    bom_dict = {}
    proc_dict = {}

    if parsed.architecture and Path(parsed.architecture).exists():
        arch_dict = json.loads(Path(parsed.architecture).read_text(encoding="utf-8"))
    if parsed.bom and Path(parsed.bom).exists():
        bom_dict = json.loads(Path(parsed.bom).read_text(encoding="utf-8"))
    if parsed.procurement and Path(parsed.procurement).exists():
        proc_dict = json.loads(Path(parsed.procurement).read_text(encoding="utf-8"))

    if not arch_dict and not bom_dict:
        # Default SAR Drone full verification bundle
        arch_dict = {
            "subsystems": [
                {"subsystem_id": "SUB-001", "name": "Edge Compute Subsystem"},
                {"subsystem_id": "SUB-002", "name": "Thermal Sensing Subsystem"},
                {"subsystem_id": "SUB-003", "name": "Power Distribution Subsystem"},
                {"subsystem_id": "SUB-004", "name": "Flight Telemetry Bridge"},
            ],
            "component_roles": [
                {"role_name": "SBC", "subsystem_id": "SUB-001"},
                {"role_name": "thermal camera", "subsystem_id": "SUB-002"},
                {"role_name": "DC-DC converter", "subsystem_id": "SUB-003"},
                {"role_name": "microcontroller", "subsystem_id": "SUB-004"},
            ],
            "interfaces": [
                {
                    "interface_id": "INT-001",
                    "source_component_id": "BOM-002",
                    "destination_component_id": "BOM-001",
                    "protocol": "VoSPI",
                    "voltage_level": 3.3,
                },
                {
                    "interface_id": "INT-002",
                    "source_component_id": "BOM-003",
                    "destination_component_id": "BOM-001",
                    "protocol": "UART",
                    "voltage_level": 3.3,
                },
            ],
            "power_domains": [
                {
                    "domain_name": "5V_MAIN",
                    "voltage_v": 5.0,
                    "max_current_capacity_a": 5.0,
                    "known_load_current_a": 3.2,
                }
            ],
        }

        bom_dict = {
            "bom_id": "BOM-SAR-001",
            "items": [
                {
                    "bom_item_id": "BOM-001",
                    "part_number": "900-13766-0000-000",
                    "component_name": "Jetson Orin Nano 8GB",
                    "category": "SBC",
                    "quantity": 1,
                    "subsystem_id": "SUB-001",
                    "known_specifications": {"operating_voltage": "5V", "logic_voltage": "3.3V", "max_current_draw": "2.5A"},
                },
                {
                    "bom_item_id": "BOM-002",
                    "part_number": "500-0771-01",
                    "component_name": "FLIR Lepton 3.5",
                    "category": "thermal camera",
                    "quantity": 1,
                    "subsystem_id": "SUB-002",
                    "known_specifications": {"operating_voltage": "3.3V", "i2c_address": "0x2A"},
                },
                {
                    "bom_item_id": "BOM-003",
                    "part_number": "ESP32-S3-WROOM-1-N8R8",
                    "component_name": "ESP32-S3 Module",
                    "category": "microcontroller",
                    "quantity": 1,
                    "subsystem_id": "SUB-004",
                    "known_specifications": {"operating_voltage": "3.3V"},
                },
                {
                    "bom_item_id": "BOM-004",
                    "part_number": "TPS565208DDCR",
                    "component_name": "5V/5A Step-Down Converter",
                    "category": "DC-DC converter",
                    "quantity": 1,
                    "subsystem_id": "SUB-003",
                    "known_specifications": {"output_voltage": "5V", "max_current_capacity": "5A"},
                },
                {
                    "bom_item_id": "BOM-005",
                    "part_number": "ECAS0D107M010K00",
                    "component_name": "1000uF Solid Polymer Capacitor",
                    "category": "capacitor",
                    "quantity": 1,
                    "subsystem_id": "SUB-003",
                },
                {
                    "bom_item_id": "BOM-006",
                    "part_number": "0297030.WXNV",
                    "component_name": "30A Blade Fuse",
                    "category": "fuse",
                    "quantity": 1,
                    "subsystem_id": "SUB-003",
                },
            ],
        }

        proc_dict = {
            "optimization_id": "OPT-SAR-001",
            "orders": [
                {
                    "order_id": "ORD-001",
                    "supplier_name": "Robu.in",
                    "items": [
                        {"bom_item_id": "BOM-001", "part_number": "900-13766-0000-000", "purchased_quantity": 1},
                        {"bom_item_id": "BOM-002", "part_number": "500-0771-01", "purchased_quantity": 1},
                        {"bom_item_id": "BOM-003", "part_number": "ESP32-S3-WROOM-1-N8R8", "purchased_quantity": 1},
                        {"bom_item_id": "BOM-004", "part_number": "TPS565208DDCR", "purchased_quantity": 1},
                        {"bom_item_id": "BOM-005", "part_number": "ECAS0D107M010K00", "purchased_quantity": 1},
                        {"bom_item_id": "BOM-006", "part_number": "0297030.WXNV", "purchased_quantity": 1},
                    ],
                }
            ],
        }

    input_data = EngineeringValidationAgentInput(
        project={"title": parsed.project, "project_id": "proj_sar_drone_001"},
        architecture=arch_dict,
        bom=bom_dict,
        optimized_procurement=proc_dict,
        output_dir=parsed.output,
    )

    agent = EngineeringValidationAgent()
    output = agent.run_sync(input_data)

    # CLI Output matching Section 50 format
    print(f"\nProject:\n{parsed.project}\n")
    print(f"Requirements:\n{len(output.requirement_results)}\n")
    print(f"Requirements Passed:\n{sum(1 for r in output.requirement_results if r.status == 'PASS')}\n")
    print(f"Requirements Failed:\n{sum(1 for r in output.requirement_results if r.status == 'FAIL')}\n")
    print(f"Requirements Unknown:\n{sum(1 for r in output.requirement_results if r.status == 'UNKNOWN')}\n")
    print(f"Architecture Checks:\n{len(output.architecture_results)}\n")
    print(f"Electrical Checks:\n{len(output.electrical_results)}\n")
    print(f"Power Checks:\n{len(output.power_results)}\n")
    print(f"Interface Checks:\n{len(output.interface_results)}\n")
    print(f"BOM Checks:\n{len(output.bom_results)}\n")
    print(f"Procurement Checks:\n{len(output.procurement_results)}\n")
    print(f"Critical Failures:\n{output.final_verdict.critical_failures}\n")
    print(f"High Failures:\n{output.final_verdict.high_failures}\n")
    print(f"Warnings:\n{output.final_verdict.warnings}\n")
    print(f"Unknowns:\n{output.final_verdict.unknowns}\n")
    print("FINAL VERDICT:\n")
    print(f"{output.verdict}\n")
    print("Reason:\n")
    print(f"{output.final_verdict.recommendation}\n")


if __name__ == "__main__":
    main()
