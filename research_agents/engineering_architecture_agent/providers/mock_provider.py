"""
Deterministic mock reasoning provider for EngineeringArchitectureAgent offline testing and CLI demo mode.
"""

from typing import Optional, Type, TypeVar
from pydantic import BaseModel
from research_agents.engineering_architecture_agent.providers.base import ReasoningProvider

T = TypeVar("T", bound=BaseModel)


class MockEngineeringArchitectureProvider(ReasoningProvider):
    """Deterministic offline reasoning provider simulating Bedrock architecture synthesis."""

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        return "Engineering architecture decomposition completed."

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: Optional[str] = None,
    ) -> T:
        # Dynamically instantiate requested schema with realistic mock fields
        data = {
            "architecture": {
                "architecture_id": "ARCH-SAR-001",
                "architecture_name": "Hybrid Edge-Compute UAV Search and Rescue Architecture",
                "description": "Hierarchical edge compute system partitioning high-throughput neural vision (Jetson Orin Nano) from real-time flight control & sensor polling (ESP32-S3).",
                "architecture_type": "Heterogeneous Edge-Controller Architecture",
                "confidence": 0.94,
            },
            "subsystems": [
                {
                    "subsystem_id": "SUB-001",
                    "name": "Compute Subsystem",
                    "purpose": "Executes real-time YOLOv8 neural inference and trajectory planning.",
                    "responsibilities": ["Image preprocessing", "TensorRT model execution", "Human detection coordinates output"],
                    "requirements": ["Real-time edge inference latency under 100ms"],
                    "components": ["NVIDIA Jetson Orin Nano 8GB"],
                    "interfaces": ["IF-001", "IF-002"],
                    "dependencies": ["DEP-001", "DEP-002"],
                    "risks": ["RISK-ARCH-001"],
                    "validation_requirements": ["VAL-ARCH-001"],
                },
                {
                    "subsystem_id": "SUB-002",
                    "name": "Sensing Subsystem",
                    "purpose": "Captures calibrated radiometric thermal LWIR images and telemetry.",
                    "responsibilities": ["Radiometric thermal frame acquisition", "I2C camera control"],
                    "requirements": ["Thermal human detection on edge hardware"],
                    "components": ["FLIR Lepton 3.5"],
                    "interfaces": ["IF-001"],
                    "dependencies": ["DEP-003"],
                    "risks": [],
                    "validation_requirements": ["VAL-ARCH-002"],
                },
                {
                    "subsystem_id": "SUB-003",
                    "name": "Power Subsystem",
                    "purpose": "Converts 4S LiPo battery voltage to stable 5V and 3.3V logic and motor rails.",
                    "responsibilities": ["Voltage regulation", "Brownout protection", "Current monitoring"],
                    "requirements": ["Battery-powered operation >= 30 minutes"],
                    "components": ["4S LiPo 5000mAh", "5V/5A Buck Regulator", "3.3V LDO"],
                    "interfaces": ["IF-PWR-001", "IF-PWR-002"],
                    "dependencies": [],
                    "risks": ["RISK-ARCH-002"],
                    "validation_requirements": ["VAL-ARCH-003"],
                },
                {
                    "subsystem_id": "SUB-004",
                    "name": "Control Subsystem",
                    "purpose": "Manages motor ESC signals, safety failsafes, and mission autopilot.",
                    "responsibilities": ["Flight stabilization", "Failsafe return-to-home", "PWM motor control"],
                    "requirements": ["Autonomous navigation in GPS-denied areas"],
                    "components": ["ESP32-S3 MCU"],
                    "interfaces": ["IF-002", "IF-003"],
                    "dependencies": ["DEP-004"],
                    "risks": [],
                    "validation_requirements": [],
                },
            ],
            "component_roles": [
                {
                    "component": "NVIDIA Jetson Orin Nano 8GB",
                    "role": "primary_edge_compute",
                    "subsystem_id": "SUB-001",
                    "status": "mandatory",
                    "reason": "Required to deliver 40 TOPS AI compute for 45 FPS thermal detection.",
                    "supporting_decision_ids": ["DEC-001"],
                    "confidence": 0.95,
                },
                {
                    "component": "FLIR Lepton 3.5",
                    "role": "radiometric_thermal_sensor",
                    "subsystem_id": "SUB-002",
                    "status": "mandatory",
                    "reason": "Provides 160x120 LWIR radiometric thermal imaging.",
                    "supporting_decision_ids": ["DEC-001"],
                    "confidence": 0.96,
                },
                {
                    "component": "ESP32-S3",
                    "role": "flight_safety_controller",
                    "subsystem_id": "SUB-004",
                    "status": "mandatory",
                    "reason": "Dedicated real-time I/O microcontroller handling motor PWM and telemetry.",
                    "supporting_decision_ids": [],
                    "confidence": 0.92,
                },
            ],
            "interfaces": [
                {
                    "interface_id": "IF-001",
                    "source": "SUB-002",
                    "target": "SUB-001",
                    "interface_type": "SPI",
                    "purpose": "Transmits raw radiometric VoSPI video stream from FLIR Lepton to Jetson.",
                    "direction": "unidirectional",
                    "voltage_logic": "3.3V",
                    "requirements": ["VoSPI protocol compliance", "14 MHz SPI clock"],
                    "constraints": ["Cable length < 15 cm to prevent signal degradation"],
                    "evidence_ids": ["ev_p_001"],
                    "confidence": 0.96,
                },
                {
                    "interface_id": "IF-002",
                    "source": "SUB-001",
                    "target": "SUB-004",
                    "interface_type": "UART",
                    "purpose": "Transmits bounding-box detections and velocity commands via micro-ROS.",
                    "direction": "bidirectional",
                    "voltage_logic": "3.3V",
                    "requirements": ["921600 baud rate"],
                    "constraints": [],
                    "evidence_ids": [],
                    "confidence": 0.94,
                },
            ],
            "power_domains": [
                {
                    "power_domain_id": "PWR-001",
                    "name": "14.8V Battery Main Rail",
                    "source": "4S LiPo Pack",
                    "voltage": "14.8V Nominal (13.0V - 16.8V)",
                    "loads": ["ESC Motor Drivers", "5V Step-Down Buck Regulator"],
                    "estimated_current": "15A Peak",
                    "regulation": "Unregulated Battery Direct",
                    "protection": ["30A Fuse", "Reverse Polarity Schottky Diode"],
                    "confidence": 0.95,
                    "validation_required": True,
                },
                {
                    "power_domain_id": "PWR-002",
                    "name": "5.0V Compute Rail",
                    "source": "Synchronous Buck Regulator",
                    "voltage": "5.0V +/- 2%",
                    "loads": ["NVIDIA Jetson Orin Nano Carrier Board"],
                    "estimated_current": "4.5A Peak",
                    "regulation": "5V/5A Switching Buck",
                    "protection": ["TVS Diode", "Current Limiting"],
                    "confidence": 0.95,
                    "validation_required": True,
                },
                {
                    "power_domain_id": "PWR-003",
                    "name": "3.3V Logic Rail",
                    "source": "3.3V LDO",
                    "voltage": "3.3V +/- 1%",
                    "loads": ["FLIR Lepton 3.5", "ESP32-S3", "IMU Sensor"],
                    "estimated_current": "600mA Peak",
                    "regulation": "Ultra-Low Noise LDO",
                    "protection": ["Decoupling Capacitors"],
                    "confidence": 0.98,
                    "validation_required": True,
                },
            ],
            "data_flows": [
                {
                    "flow_id": "DATA-001",
                    "source": "FLIR Lepton 3.5 (SUB-002)",
                    "destination": "NVIDIA Jetson Orin Nano (SUB-001)",
                    "data_type": "VoSPI 14-bit Thermal Video Frames",
                    "protocol": "SPI (14 MHz)",
                    "direction": "unidirectional",
                    "latency_requirement": "< 20 ms",
                    "bandwidth_requirement": "160x120 @ 8.7 Hz (~2.5 Mbps)",
                    "evidence_ids": ["ev_p_001"],
                },
                {
                    "flow_id": "DATA-002",
                    "source": "NVIDIA Jetson Orin Nano (SUB-001)",
                    "destination": "ESP32-S3 Controller (SUB-004)",
                    "data_type": "Target Bounding Box Coordinates & Velocity Vector",
                    "protocol": "micro-ROS / UART",
                    "direction": "unidirectional",
                    "latency_requirement": "< 10 ms",
                    "bandwidth_requirement": "50 Hz message stream",
                    "evidence_ids": [],
                },
            ],
            "control_flows": [
                {
                    "control_id": "CTRL-001",
                    "control_source": "NVIDIA Jetson Orin Nano",
                    "control_target": "ESP32-S3 Flight Autopilot",
                    "trigger": "Human Target Acquired",
                    "decision_stage": "Target Tracking Loiter Command",
                    "feedback_path": "ESP32 telemetry confirms loiter coordinates",
                }
            ],
            "feedback_loops": [
                {
                    "loop_id": "LOOP-001",
                    "type": "closed_loop_control",
                    "sensor": "FLIR Lepton 3.5 Thermal Sensor",
                    "controller": "Jetson Orin Nano Vision Tracker",
                    "actuator": "Drone Pan-Tilt Gimbal Servos",
                    "feedback_signal": "Centroid pixel error vector",
                    "validation_required": True,
                }
            ],
            "software_architecture": [
                {
                    "layer_id": "SW-001",
                    "name": "Hardware Drivers & BSP",
                    "responsibilities": ["V4L2 Video Driver", "SPI VoSPI DMA Receiver", "UART Serial Driver"],
                    "technologies": ["Linux JetPack 6.0", "ESP-IDF v5.1"],
                },
                {
                    "layer_id": "SW-002",
                    "name": "Middleware & Messaging",
                    "responsibilities": ["Inter-process communication", "Node lifecycle management", "Telemetry publishing"],
                    "technologies": ["ROS 2 Humble", "micro-ROS"],
                },
                {
                    "layer_id": "SW-003",
                    "name": "AI Inference Engine",
                    "responsibilities": ["TensorRT FP16/INT8 inference", "NMS Postprocessing", "Centroid extraction"],
                    "technologies": ["TensorRT 8.6", "CUDA 12.2", "YOLOv8n-pose"],
                },
                {
                    "layer_id": "SW-004",
                    "name": "Autopilot & Mission Logic",
                    "responsibilities": ["Waypoint navigation", "Search pattern generation", "Failsafe geofence monitor"],
                    "technologies": ["PX4 / Custom C++ State Machine"],
                },
            ],
            "hardware_software_boundary": {
                "hardware_responsibilities": ["Optical thermal sensing", "DC-DC power conversion", "Motor actuation"],
                "firmware_responsibilities": ["Real-time PWM signal generation", "Hardware watchdog timer", "SPI frame capture DMA"],
                "software_responsibilities": ["Thermal radiometric calibration", "Coordinate frame transformation", "ROS 2 node graph"],
                "ai_responsibilities": ["Human pose detection", "Confidence thresholding", "Bounding box regression"],
                "cloud_responsibilities": ["Telemetry archival", "Base station mission dashboard map sync"],
            },
            "physical_architecture": [
                {
                    "element_id": "PHYS-001",
                    "category": "sensor_placement",
                    "description": "Downward/forward 45-degree vibration-damped nose mount for FLIR Lepton camera.",
                    "constraints": ["Clear field of view unobstructed by landing gear or prop wash."],
                },
                {
                    "element_id": "PHYS-002",
                    "category": "compute_placement",
                    "description": "Central fuselage payload bay mount for Jetson Orin Nano with ducting from propeller airflow.",
                    "constraints": ["Must align center of gravity within 5 mm of airframe center."],
                },
            ],
            "thermal_architecture": [
                {
                    "thermal_element_id": "THERM-001",
                    "source": "NVIDIA Jetson Orin Nano (15 W Peak Load)",
                    "thermal_risk": "Thermal throttling when operating in 40 deg C ambient desert conditions.",
                    "mitigation": "Anodized aluminum finned heatsink coupled with propeller downdraft ducting.",
                    "validation_required": True,
                }
            ],
            "communication_architecture": [
                {
                    "interface_id": "IF-COMM-001",
                    "source": "ESP32-S3 (SUB-004)",
                    "target": "Ground Control Base Station",
                    "interface_type": "Wi-Fi",
                    "purpose": "Long-range 2.4 GHz telemetry and status downlink.",
                    "direction": "bidirectional",
                    "voltage_logic": "Wireless",
                    "requirements": ["Range >= 300m", "MAVLink protocol"],
                    "constraints": [],
                    "evidence_ids": [],
                    "confidence": 0.92,
                }
            ],
            "dependencies": [
                {
                    "dependency_id": "DEP-001",
                    "source": "Compute Subsystem (SUB-001)",
                    "dependency_type": "power",
                    "target": "5.0V Compute Rail (PWR-002)",
                    "description": "Jetson Orin Nano requires stable 5.0V +/- 2% at up to 4.5A peak.",
                    "mandatory": True,
                    "validation_required": True,
                },
                {
                    "dependency_id": "DEP-002",
                    "source": "Compute Subsystem (SUB-001)",
                    "dependency_type": "communication",
                    "target": "Sensing Subsystem (SUB-002)",
                    "description": "Jetson depends on continuous VoSPI data stream from FLIR Lepton.",
                    "mandatory": True,
                    "validation_required": True,
                },
                {
                    "dependency_id": "DEP-003",
                    "source": "Sensing Subsystem (SUB-002)",
                    "dependency_type": "power",
                    "target": "3.3V Logic Rail (PWR-003)",
                    "description": "FLIR Lepton operates on filtered 3.3V low-noise supply.",
                    "mandatory": True,
                    "validation_required": True,
                },
            ],
            "architecture_decisions": [
                {
                    "architecture_decision_id": "ARCH-DEC-001",
                    "decision_area": "System Compute Partitioning",
                    "selected_architecture": "Heterogeneous Dual-Compute (Jetson Orin Nano for Vision + ESP32-S3 for Autopilot)",
                    "alternatives": ["Single monolithic SBC running Linux for both vision and flight control", "Fully distributed microcontrollers without AI"],
                    "reason": "Separates safety-critical real-time flight control from heavy non-deterministic GPU Linux inference workloads.",
                    "supporting_decision_ids": ["DEC-001"],
                    "supporting_evidence_ids": ["ev_p_001", "ev_w_001"],
                    "confidence": 0.95,
                    "validation_required": True,
                }
            ],
            "alternatives": [
                {
                    "alternative_id": "ALT-001",
                    "name": "Monolithic Compute Architecture",
                    "description": "Run both computer vision and flight stabilization software on Raspberry Pi 5 Linux OS.",
                    "tradeoff_analysis": {"latency": "Unpredictable OS jitter > 50ms", "cost": "Lower cost", "safety": "High risk of crash on kernel lockup"},
                    "selected": False,
                }
            ],
            "risks": [
                {
                    "risk_id": "ARCH-RISK-001",
                    "category": "thermal",
                    "description": "Jetson Orin Nano overheating inside enclosed fuselage during summer hover search.",
                    "affected_subsystems": ["SUB-001"],
                    "likelihood": "medium",
                    "impact": "high",
                    "mitigation": "Incorporate forced-air ducting from drone propeller downdraft directly over heatsink.",
                    "validation_required": True,
                },
                {
                    "risk_id": "ARCH-RISK-002",
                    "category": "power",
                    "description": "High instantaneous GPU current burst causing voltage droop on the 5V bus.",
                    "affected_subsystems": ["SUB-001", "SUB-003"],
                    "likelihood": "medium",
                    "impact": "high",
                    "mitigation": "Add 1000uF low-ESR solid polymer capacitor at the Jetson power input connector.",
                    "validation_required": True,
                },
            ],
            "validation_requirements": [
                {
                    "validation_id": "VAL-ARCH-001",
                    "category": "electrical",
                    "description": "Measure 3.3V and 5.0V rail voltage ripple under full GPU and motor load simultaneously.",
                    "acceptance_criteria": "Voltage ripple < 50 mVpp; no brownout reset across 30 minutes.",
                    "affected_subsystem_ids": ["SUB-001", "SUB-003"],
                },
                {
                    "validation_id": "VAL-ARCH-002",
                    "category": "communication",
                    "description": "Verify zero SPI VoSPI packet drops between FLIR Lepton and Jetson over 10,000 frames.",
                    "acceptance_criteria": "Packet drop rate < 0.01% with CRC integrity maintained.",
                    "affected_subsystem_ids": ["SUB-001", "SUB-002"],
                },
            ],
            "traceability": [
                {
                    "traceability_id": "TRACE-ARCH-001",
                    "requirement_ids": ["REQ-001", "REQ-002"],
                    "engineering_decision_ids": ["DEC-001"],
                    "architecture_decision_ids": ["ARCH-DEC-001"],
                    "subsystem_ids": ["SUB-001", "SUB-002"],
                    "component_ids": ["NVIDIA Jetson Orin Nano 8GB", "FLIR Lepton 3.5"],
                    "interface_ids": ["IF-001", "IF-002"],
                    "validation_ids": ["VAL-ARCH-001", "VAL-ARCH-002"],
                }
            ],
            "block_diagram": {
                "nodes": [
                    {"id": "NODE-001", "type": "sensor", "label": "FLIR Lepton 3.5", "subsystem": "SUB-002"},
                    {"id": "NODE-002", "type": "compute", "label": "NVIDIA Jetson Orin Nano", "subsystem": "SUB-001"},
                    {"id": "NODE-003", "type": "controller", "label": "ESP32-S3 Autopilot", "subsystem": "SUB-004"},
                    {"id": "NODE-004", "type": "power", "label": "5V/5A Buck Regulator", "subsystem": "SUB-003"},
                ],
                "edges": [
                    {"source": "NODE-001", "target": "NODE-002", "type": "data", "label": "SPI (VoSPI)"},
                    {"source": "NODE-002", "target": "NODE-003", "type": "control", "label": "UART (micro-ROS)"},
                    {"source": "NODE-004", "target": "NODE-002", "type": "power", "label": "5.0V @ 4.5A"},
                ],
            },
            "architecture_graph": {
                "nodes": [
                    {"id": "proj_sar_drone", "type": "project", "label": "Autonomous Search and Rescue Drone"},
                    {"id": "SUB-001", "type": "subsystem", "label": "Compute Subsystem"},
                    {"id": "SUB-002", "type": "subsystem", "label": "Sensing Subsystem"},
                    {"id": "SUB-003", "type": "subsystem", "label": "Power Subsystem"},
                    {"id": "SUB-004", "type": "subsystem", "label": "Control Subsystem"},
                    {"id": "comp_jetson", "type": "component", "label": "NVIDIA Jetson Orin Nano"},
                    {"id": "comp_lepton", "type": "component", "label": "FLIR Lepton 3.5"},
                    {"id": "IF-001", "type": "interface", "label": "SPI VoSPI Interface"},
                ],
                "edges": [
                    {"source": "proj_sar_drone", "target": "SUB-001", "relationship": "contains"},
                    {"source": "proj_sar_drone", "target": "SUB-002", "relationship": "contains"},
                    {"source": "SUB-001", "target": "comp_jetson", "relationship": "contains"},
                    {"source": "SUB-002", "target": "comp_lepton", "relationship": "contains"},
                    {"source": "comp_lepton", "target": "comp_jetson", "relationship": "communicates_with"},
                ],
            },
            "component_requirements": [
                {
                    "category": "Edge AI Compute Module",
                    "quantity": 1,
                    "required_specs": ["NVIDIA Ampere architecture", ">= 40 TOPS", "8GB LPDDR5", "SPI & UART headers"],
                    "reason": "Host for TensorRT real-time vision model.",
                    "source_subsystem": "SUB-001",
                },
                {
                    "category": "Radiometric Thermal Sensor",
                    "quantity": 1,
                    "required_specs": ["160x120 LWIR resolution", "SPI VoSPI video", "I2C control", "3.3V supply"],
                    "reason": "Captures calibrated ground thermal signatures.",
                    "source_subsystem": "SUB-002",
                },
            ],
            "assumptions": [
                {"assumption": "Sensor cabling length will not exceed 15 cm within the fuselage airframe.", "impact": "Enables 14 MHz single-ended SPI without differential transceivers."}
            ],
            "unknowns": [
                {"unknown": "Exact RF attenuation of telemetry signal when flying behind dense concrete structures.", "why_it_matters": "Determines need for secondary 915 MHz long-range radio fallback."}
            ],
        }

        return schema.model_validate(data)
