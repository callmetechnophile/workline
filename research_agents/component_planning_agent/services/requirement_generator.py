"""
Component requirement generation service for ComponentPlanningAgent (Section 7).
Derives technical specifications and component categories from system architecture.
"""

from typing import Any, Dict, List
from research_agents.component_planning_agent.schemas import ComponentRequirementItem, ProjectMeta


class ComponentRequirementGenerator:
    """Generates technical component requirements from architecture subsystems and roles."""

    def generate_requirements(
        self,
        project: ProjectMeta,
        subsystems: List[Dict[str, Any]],
        component_roles: List[Dict[str, Any]],
        power_domains: List[Dict[str, Any]],
        engineering_decisions: List[Dict[str, Any]],
    ) -> List[ComponentRequirementItem]:
        """
        Derives component requirements from architecture domains.
        """
        requirements: List[ComponentRequirementItem] = []

        # 1. Edge AI Compute Requirement
        requirements.append(
            ComponentRequirementItem(
                requirement_id="COMP-REQ-001",
                category="SBC",
                quantity=1,
                required_specifications={
                    "ai_compute": ">= 40 TOPS",
                    "memory": ">= 8 GB LPDDR5",
                    "operating_voltage": "5.0 V DC",
                    "interfaces": ["SPI", "UART", "I2C", "CSI", "USB 3.2"],
                },
                source_subsystem="SUB-001",
                reason="Provides host execution environment for 45 FPS YOLOv8 neural vision model.",
                source_decision_ids=["DEC-001"],
            )
        )

        # 2. Thermal Camera Core Requirement
        requirements.append(
            ComponentRequirementItem(
                requirement_id="COMP-REQ-002",
                category="thermal camera",
                quantity=1,
                required_specifications={
                    "resolution": ">= 160x120",
                    "spectral_band": "LWIR 8-14 um",
                    "radiometric": True,
                    "video_interface": "SPI VoSPI",
                },
                source_subsystem="SUB-002",
                reason="Enables human heat signature detection in unlit, smoke, and foliage environments.",
                source_decision_ids=["DEC-001"],
            )
        )

        # 3. Flight Controller / Microcontroller Requirement
        requirements.append(
            ComponentRequirementItem(
                requirement_id="COMP-REQ-003",
                category="microcontroller",
                quantity=1,
                required_specifications={
                    "core_frequency": ">= 240 MHz",
                    "wireless": "Wi-Fi + BLE",
                    "pwm_channels": ">= 4",
                    "operating_voltage": "3.3 V",
                },
                source_subsystem="SUB-004",
                reason="Dedicated real-time controller for ESC PWM generation and micro-ROS telemetry.",
                source_decision_ids=[],
            )
        )

        # 4. Power Regulator Requirement
        requirements.append(
            ComponentRequirementItem(
                requirement_id="COMP-REQ-004",
                category="DC-DC converter",
                quantity=1,
                required_specifications={
                    "input_voltage": "14.8 V Nominal (4S LiPo)",
                    "output_voltage": "5.0 V",
                    "output_current": ">= 4.5 A",
                    "topology": "Synchronous Step-Down Buck",
                },
                source_subsystem="SUB-003",
                reason="Steps down 4S battery voltage to 5.0V compute rail for Jetson module.",
                source_decision_ids=[],
            )
        )

        return requirements
