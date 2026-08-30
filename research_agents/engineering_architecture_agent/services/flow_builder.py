"""
Data flow, control hierarchy, and feedback loop builder for EngineeringArchitectureAgent (Sections 15, 16, 17, 18).
"""

from typing import List, Tuple
from research_agents.engineering_architecture_agent.schemas import (
    ControlFlowItem,
    DataFlowItem,
    FeedbackLoopItem,
    SubsystemItem,
)


class FlowBuilder:
    """Constructs explicit data pathways, control hierarchies, and closed-loop feedback systems."""

    def build_flows(
        self,
        subsystems: List[SubsystemItem],
    ) -> Tuple[List[DataFlowItem], List[ControlFlowItem], List[FeedbackLoopItem]]:
        """
        Synthesizes structured data flows, control flows, and closed-loop feedback loops.
        """
        data_flows: List[DataFlowItem] = []
        control_flows: List[ControlFlowItem] = []
        feedback_loops: List[FeedbackLoopItem] = []

        # 1. Data Flows (Section 16)
        data_flows.append(
            DataFlowItem(
                flow_id="DATA-001",
                source="FLIR Lepton 3.5 (SUB-002)",
                destination="NVIDIA Jetson Orin Nano (SUB-001)",
                data_type="14-bit Radiometric Raw LWIR Frames",
                protocol="SPI (VoSPI Protocol)",
                direction="unidirectional",
                latency_requirement="< 25 ms",
                bandwidth_requirement="160x120 @ 8.7 Hz (~2.5 Mbps)",
                evidence_ids=["ev_p_001"],
            )
        )

        data_flows.append(
            DataFlowItem(
                flow_id="DATA-002",
                source="NVIDIA Jetson Orin Nano (SUB-001)",
                destination="ESP32-S3 Controller (SUB-004)",
                data_type="Target Bounding Box Coordinates & Centroid Offsets",
                protocol="UART / micro-ROS",
                direction="unidirectional",
                latency_requirement="< 10 ms",
                bandwidth_requirement="50 Hz messages (~100 kbps)",
                evidence_ids=[],
            )
        )

        # 2. Control Flows (Section 17)
        control_flows.append(
            ControlFlowItem(
                control_id="CTRL-001",
                control_source="Jetson Orin Nano Vision Pipeline",
                control_target="ESP32-S3 Autopilot State Machine",
                trigger="High-Confidence Human Detection (Confidence >= 0.85)",
                decision_stage="Switch from Area Search to Target-Centric Loiter Mode",
                feedback_path="ESP32 telemetry confirms loiter radius & altitude hold",
            )
        )

        # 3. Closed-Loop Feedback Loops (Section 18)
        feedback_loops.append(
            FeedbackLoopItem(
                loop_id="LOOP-001",
                type="closed_loop_control",
                sensor="FLIR Lepton 3.5 Thermal Core",
                controller="Jetson Orin Nano Centroid Tracker",
                actuator="Gimbal Yaw/Pitch Servos",
                feedback_signal="Pixel Centroid Error Vector (dx, dy)",
                validation_required=True,
            )
        )

        return data_flows, control_flows, feedback_loops
