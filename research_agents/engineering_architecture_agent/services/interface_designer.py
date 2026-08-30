"""
Interface design and electrical bus architecture service for EngineeringArchitectureAgent (Sections 10, 11, 12).
"""

from typing import List
from research_agents.engineering_architecture_agent.schemas import InterfaceItem, SubsystemItem


class InterfaceDesigner:
    """Designs communication, electrical, and physical interfaces between subsystems."""

    def design_interfaces(
        self,
        subsystems: List[SubsystemItem],
    ) -> List[InterfaceItem]:
        """
        Synthesizes structured interfaces interconnecting subsystems.
        """
        interfaces: List[InterfaceItem] = []

        # 1. SPI Video Interface (Sensing -> Compute)
        interfaces.append(
            InterfaceItem(
                interface_id="IF-001",
                source="SUB-002",  # Sensing
                target="SUB-001",  # Compute
                interface_type="SPI",
                purpose="Stream 14-bit VoSPI thermal video frames from FLIR Lepton to Jetson Orin Nano.",
                direction="unidirectional",
                voltage_logic="3.3V",
                requirements=["SPI Mode 3", "14 MHz clock rate", "CS active low"],
                constraints=["Trace length < 150 mm", "Ground plane shielding"],
                evidence_ids=["ev_p_001"],
                confidence=0.96,
            )
        )

        # 2. UART Command / Telemetry Interface (Compute <-> Control)
        interfaces.append(
            InterfaceItem(
                interface_id="IF-002",
                source="SUB-001",  # Compute
                target="SUB-004",  # Control
                interface_type="UART",
                purpose="Exchange micro-ROS target coordinates, trajectory commands, and telemetry.",
                direction="bidirectional",
                voltage_logic="3.3V",
                requirements=["921600 baud", "8-N-1 format", "Hardware flow control RTS/CTS"],
                constraints=[],
                evidence_ids=[],
                confidence=0.94,
            )
        )

        # 3. I2C Camera Configuration Interface (Compute -> Sensing)
        interfaces.append(
            InterfaceItem(
                interface_id="IF-003",
                source="SUB-001",  # Compute
                target="SUB-002",  # Sensing
                interface_type="I2C",
                purpose="Configure FLIR Lepton telemetry parameters, FFC shutter cycles, and gain mode.",
                direction="bidirectional",
                voltage_logic="3.3V",
                requirements=["400 kHz Fast-Mode I2C", "2.2k pull-up resistors"],
                constraints=[],
                evidence_ids=[],
                confidence=0.95,
            )
        )

        # 4. PWM Motor Actuation Interface (Control -> Actuators)
        interfaces.append(
            InterfaceItem(
                interface_id="IF-004",
                source="SUB-004",  # Control
                target="SUB-003",  # Actuation / Power
                interface_type="PWM",
                purpose="Drive electronic speed controllers (ESCs) via DShot600 digital protocol.",
                direction="unidirectional",
                voltage_logic="3.3V",
                requirements=["DShot600 or 400 Hz standard PWM"],
                constraints=[],
                evidence_ids=[],
                confidence=0.95,
            )
        )

        return interfaces
