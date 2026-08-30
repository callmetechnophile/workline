"""
Software architecture and hardware/software boundary service for EngineeringArchitectureAgent (Sections 19 & 20).
"""

from typing import List, Tuple
from research_agents.engineering_architecture_agent.schemas import (
    HardwareSoftwareBoundary,
    SoftwareLayerItem,
    SubsystemItem,
)


class SoftwareArchitect:
    """Architects layered software stack and delineates hardware/software boundaries."""

    def design_software_stack(
        self,
        subsystems: List[SubsystemItem],
    ) -> Tuple[List[SoftwareLayerItem], HardwareSoftwareBoundary]:
        """
        Synthesizes software stack layers and boundary mappings.
        """
        layers: List[SoftwareLayerItem] = []

        layers.append(
            SoftwareLayerItem(
                layer_id="SW-001",
                name="Hardware Abstraction Layer & Drivers",
                responsibilities=["V4L2 Video Driver", "SPI VoSPI DMA Receiver", "UART Serial Driver", "I2C Sensor HAL"],
                technologies=["Linux JetPack 6.0 BSP", "ESP-IDF v5.1 HAL"],
            )
        )

        layers.append(
            SoftwareLayerItem(
                layer_id="SW-002",
                name="Middleware & IPC",
                responsibilities=["Publish/Subscribe node graph", "micro-ROS Agent/Client", "Telemetry logging"],
                technologies=["ROS 2 Humble", "micro-ROS", "eProsima FastDDS"],
            )
        )

        layers.append(
            SoftwareLayerItem(
                layer_id="SW-003",
                name="AI Inference & Perception",
                responsibilities=["YOLOv8n-pose TensorRT INT8 execution", "Non-Maximum Suppression (NMS)", "Centroid tracking"],
                technologies=["NVIDIA TensorRT 8.6", "CUDA 12.2", "OpenCV 4.8"],
            )
        )

        layers.append(
            SoftwareLayerItem(
                layer_id="SW-004",
                name="Mission Logic & Autopilot Interface",
                responsibilities=["Search lawnmower pattern planner", "Failsafe geofence monitor", "MAVLink command translator"],
                technologies=["PX4 Autopilot / Custom C++ State Machine"],
            )
        )

        boundary = HardwareSoftwareBoundary(
            hardware_responsibilities=[
                "Optical LWIR thermal photon sensing",
                "DC-DC power rail regulation & protection",
                "Motor electrical phase switching",
            ],
            firmware_responsibilities=[
                "Real-time PWM timer generation for ESCs",
                "Hardware watchdog and brownout detection",
                "DMA-based VoSPI thermal frame buffer acquisition",
            ],
            software_responsibilities=[
                "Thermal radiometric span & gain calibration",
                "Coordinate transformation (Camera Frame -> Drone Body Frame -> Global GPS)",
                "ROS 2 node graph message lifecycle management",
            ],
            ai_responsibilities=[
                "Human keypoint pose estimation and bounding box detection",
                "Temporal confidence thresholding across sequential frames",
            ],
            cloud_responsibilities=[
                "Mission telemetry log storage and base station map visualization",
            ],
        )

        return layers, boundary
