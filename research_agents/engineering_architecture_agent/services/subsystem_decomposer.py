"""
Subsystem decomposition service for EngineeringArchitectureAgent (Sections 6 & 7).
Decomposes engineering projects into structured subsystem domains with explicit responsibilities.
"""

from typing import Any, Dict, List
from research_agents.engineering_architecture_agent.schemas import ProjectMeta, SubsystemItem


class SubsystemDecomposer:
    """Decomposes an engineering project into logical subsystems."""

    def decompose(
        self,
        project: ProjectMeta,
        decisions: List[Dict[str, Any]],
        requirements: List[str],
    ) -> List[SubsystemItem]:
        """
        Synthesizes structured subsystems based on project domain and requirements.
        """
        subsystems: List[SubsystemItem] = []
        domain_lower = (project.engineering_domain or "").lower()
        title_lower = project.title.lower()

        # 1. Compute Subsystem
        subsystems.append(
            SubsystemItem(
                subsystem_id="SUB-001",
                name="Compute Subsystem",
                purpose="Executes real-time neural inference, computer vision, and coordinate mapping.",
                responsibilities=["Process sensor data", "Run AI/ML models", "Publish control telemetry"],
                requirements=[r for r in requirements if any(k in r.lower() for k in ["inference", "compute", "real-time", "latency"])],
                components=["NVIDIA Jetson Orin Nano 8GB"],
                interfaces=["IF-001", "IF-002"],
                dependencies=["DEP-001", "DEP-002"],
                risks=["ARCH-RISK-001"],
                validation_requirements=["VAL-ARCH-001"],
            )
        )

        # 2. Sensing Subsystem
        subsystems.append(
            SubsystemItem(
                subsystem_id="SUB-002",
                name="Sensing Subsystem",
                purpose="Captures environmental telemetry, radiometric thermal imagery, and flight kinematics.",
                responsibilities=["Acquire thermal images", "Sample IMU kinematics", "Calibrate sensor readings"],
                requirements=[r for r in requirements if any(k in r.lower() for k in ["thermal", "sensor", "camera", "detect"])],
                components=["FLIR Lepton 3.5"],
                interfaces=["IF-001"],
                dependencies=["DEP-003"],
                risks=[],
                validation_requirements=["VAL-ARCH-002"],
            )
        )

        # 3. Power Subsystem
        subsystems.append(
            SubsystemItem(
                subsystem_id="SUB-003",
                name="Power Subsystem",
                purpose="Manages energy storage, DC-DC voltage regulation, and transient protection.",
                responsibilities=["Provide regulated 5.0V and 3.3V rails", "Protect against brownouts", "Monitor battery level"],
                requirements=[r for r in requirements if any(k in r.lower() for k in ["power", "battery", "voltage", "endurance"])],
                components=["4S LiPo 5000mAh Battery", "5V/5A Buck Regulator", "3.3V Low-Noise LDO"],
                interfaces=["IF-PWR-001", "IF-PWR-002"],
                dependencies=[],
                risks=["ARCH-RISK-002"],
                validation_requirements=["VAL-ARCH-001"],
            )
        )

        # 4. Control Subsystem
        subsystems.append(
            SubsystemItem(
                subsystem_id="SUB-004",
                name="Control Subsystem",
                purpose="Executes real-time flight stabilization, trajectory execution, and safety failsafes.",
                responsibilities=["Generate PWM motor outputs", "Handle autopilot state machine", "Enforce safety geofences"],
                requirements=[r for r in requirements if any(k in r.lower() for k in ["control", "navigation", "autonomous", "flight"])],
                components=["ESP32-S3 Microcontroller"],
                interfaces=["IF-002", "IF-003"],
                dependencies=["DEP-004"],
                risks=[],
                validation_requirements=[],
            )
        )

        return subsystems
