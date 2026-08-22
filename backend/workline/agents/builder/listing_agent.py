"""Listing Agent: Generates candidate hardware component lists across system categories."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.shared.prompts import LISTING_AGENT_PROMPT
from backend.workline.agents.shared.schemas import (
    AgentFinding,
    AgentOutput,
    CandidateComponent,
)
from backend.workline.agents.shared.tools import WorklineToolSuite


class ListingAgent:
    """Specialist agent producing candidate component selections."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "listing_agent"
        self.prompt = LISTING_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Propose candidate components for the project."""
        candidates = [
            CandidateComponent(
                category="Microcontroller",
                name="ESP32-S3-WROOM-1",
                part_number="ESP32-S3-WROOM-1-N8R8",
                vendor="Espressif",
                description="Dual-core Xtensa LX7 MCU with 2.4GHz Wi-Fi and Bluetooth 5 LE",
                estimated_price_usd=3.50,
                specifications={"core": "Dual LX7", "flash_mb": 8, "psram_mb": 8, "vdd_v": 3.3},
            ),
            CandidateComponent(
                category="Sensor",
                name="MPU-6050",
                part_number="MPU-6050",
                vendor="TDK InvenSense",
                description="6-axis MotionTracking device with 3-axis gyroscope and 3-axis accelerometer",
                estimated_price_usd=2.10,
                specifications={"interface": "I2C", "voltage_range": "2.375V-3.46V"},
            ),
            CandidateComponent(
                category="Sensor",
                name="BME280",
                part_number="BME280",
                vendor="Bosch Sensortec",
                description="Combined humidity, pressure, and temperature sensor",
                estimated_price_usd=3.20,
                specifications={"interface": "I2C/SPI", "voltage_range": "1.71V-3.6V"},
            ),
            CandidateComponent(
                category="Motor Driver",
                name="DRV8833",
                part_number="DRV8833PWPR",
                vendor="Texas Instruments",
                description="Dual H-Bridge Motor Driver IC with current limit protection",
                estimated_price_usd=1.45,
                specifications={"vm_range": "2.7V-10.8V", "max_current_a": 1.5},
            ),
            CandidateComponent(
                category="Power",
                name="TPS62840",
                part_number="TPS62840DLYR",
                vendor="Texas Instruments",
                description="750mA ultra-low Iq (60nA) step-down converter",
                estimated_price_usd=1.15,
                specifications={"vin_range": "1.8V-6.5V", "vout_v": 3.3, "efficiency": 0.95},
            ),
        ]

        # Persist candidate nodes into SurrealDB
        for c in candidates:
            await self.tools.save_graph_node(
                node_id=f"candidate:{project_id}_{c.name.lower().replace('-', '_').replace(' ', '_')}",
                node_type="CandidateComponent",
                label=c.name,
                data=c.model_dump(),
            )

        findings = [
            AgentFinding(
                category="Component Selection",
                title="Candidates Identified",
                detail=f"Identified {len(candidates)} candidate components across MCU, Sensor, Driver, and Power domains.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="component_selection",
            summary=f"Listed {len(candidates)} candidate components ready for ranking and validation.",
            findings=findings,
            data={"candidates": [c.model_dump() for c in candidates]},
        )
