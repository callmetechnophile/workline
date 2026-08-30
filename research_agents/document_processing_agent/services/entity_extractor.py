"""
Explicit engineering entity extraction service for DocumentProcessingAgent.
Detects microcontrollers, sensors, actuators, protocols, compute modules, interfaces, and algorithms.
"""

import re
from typing import List, Set, Tuple
from research_agents.document_processing_agent.schemas import (
    EngineeringEntity,
    ExtractedBlock,
)


class EngineeringEntityExtractor:
    """Extracts verified hardware/software engineering entity mentions from text blocks."""

    ENTITY_TAXONOMY = {
        "microcontroller": [
            r"\b(ESP32(-S[23]|-C[36])?|STM32[FGH]\d{3}|RP2040|ATmega328P?|SAMD21|nRF52840|TMS320|MSP430)\b",
            r"\b(Jetson\s*(Orin(\s*Nano)?|Xavier|Nano)|Raspberry\s*Pi(\s*[45]|Pico)?|BeagleBone|Arduino\s*(Uno|Mega|Nano)?)\b",
        ],
        "sensor": [
            r"\b(MPU-?6050|MPU-?9250|BME280|BMP280|VL53L\d[A-Z]?|FLIR\s*(Lepton|Boson)?|IMU|LiDAR|IMX\d{3}|OV\d{4})\b",
            r"\b(thermal\s*camera|ultrasonic\s*sensor|accelerometer|gyroscope|magnetometer|barometer)\b",
        ],
        "protocol_or_interface": [
            r"\b(I2C|SPI|UART|CAN\s*(bus|FD)?|RS-?485|USB-C|PCIe\s*(Gen\s*\d)?|PWM|DShot|MAVLink|Ethernet|Wi-Fi|Bluetooth\s*(LE)?|LoRa(WAN)?)\b",
        ],
        "software_framework": [
            r"\b(ROS\s*2\s*(Humble|Iron|Jazzy)?|ROS|FreeRTOS|Zephyr|TensorRT|OpenCV|PyTorch|TensorFlow|YOLOv\d+|PX4|ArduPilot)\b",
        ],
        "power_system": [
            r"\b(buck\s*converter|boost\s*converter|LDO|LiPo\s*(\d+S)?|BMS|MOSFET|GaN|IGBT)\b",
        ],
    }

    def extract_entities(self, blocks: List[ExtractedBlock]) -> List[EngineeringEntity]:
        """
        Scans document text blocks and extracts engineering entities with page provenance.
        """
        entities: List[EngineeringEntity] = []
        seen_keys: Set[Tuple[str, int]] = set()

        for b in blocks:
            text = b.text
            for category, patterns in self.ENTITY_TAXONOMY.items():
                for pat in patterns:
                    for match in re.finditer(pat, text, re.IGNORECASE):
                        entity_name = match.group(0).strip()
                        key = (entity_name.lower(), b.page_number)
                        if key in seen_keys:
                            continue
                        seen_keys.add(key)

                        snippet_start = max(0, match.start() - 30)
                        snippet_end = min(len(text), match.end() + 30)
                        snippet = text[snippet_start:snippet_end].replace("\n", " ").strip()

                        # Candidate relationship detection if two entities appear in close context
                        rel_candidate = None
                        if category == "microcontroller" and ("with" in snippet.lower() or "connect" in snippet.lower() or "over" in snippet.lower()):
                            rel_candidate = "connected_device"

                        entities.append(
                            EngineeringEntity(
                                name=entity_name,
                                category=category,
                                page_number=b.page_number,
                                context_snippet=snippet,
                                candidate_relationship=rel_candidate,
                            )
                        )

        return entities
