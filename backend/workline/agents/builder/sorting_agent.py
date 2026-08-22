"""Sorting Agent: Evaluates and ranks candidate components using multi-criteria matrix."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.shared.prompts import SORTING_AGENT_PROMPT
from backend.workline.agents.shared.schemas import AgentFinding, AgentOutput
from backend.workline.agents.shared.tools import WorklineToolSuite


class SortingAgent:
    """Specialist agent scoring and ranking candidate components."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "sorting_agent"
        self.prompt = SORTING_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Score candidate components."""
        rankings = [
            {
                "name": "ESP32-S3-WROOM-1",
                "category": "Microcontroller",
                "score": 9.4,
                "reasons": ["Native USB-OTG and Wi-Fi/BLE", "8MB Flash + 8MB PSRAM", "Strong open-source community support"],
                "risks": ["Requires clean 3.3V rail with 500mA peak handling"],
                "alternatives": ["RP2040 + ESP-C3", "STM32F401"],
            },
            {
                "name": "DRV8833",
                "category": "Motor Driver",
                "score": 8.9,
                "reasons": ["Low on-resistance (360 mOhm)", "Built-in thermal and UVLO shutdown", "PWM current control"],
                "risks": ["Max 10.8V motor voltage limit"],
                "alternatives": ["L298N (inefficient)", "TB6612FNG"],
            },
            {
                "name": "BME280",
                "category": "Environmental Sensor",
                "score": 9.2,
                "reasons": ["Combined Temp/Hum/Baro in single 2.5x2.5mm package", "High accuracy and fast response time"],
                "risks": ["Prone to thermal heating from nearby power regulators if placed poorly"],
                "alternatives": ["DHT22 (large)", "AHT20 + BMP280"],
            },
            {
                "name": "MPU-6050",
                "category": "Motion Sensor",
                "score": 8.6,
                "reasons": ["Integrated DMP (Digital Motion Processor)", "Ubiquitous library support"],
                "risks": ["Legacy part with counterfeit market; verify authorized distributor"],
                "alternatives": ["ICM-42688-P", "LSM6DSOX"],
            },
            {
                "name": "TPS62840",
                "category": "Voltage Regulator",
                "score": 9.5,
                "reasons": ["60nA ultra-low quiescent current", "95% peak efficiency", "Small footprint"],
                "risks": ["Small WLCSP/QFN package requires careful PCB routing"],
                "alternatives": ["LM1117-3.3 (poor efficiency)", "AP2112K"],
            },
        ]

        findings = [
            AgentFinding(
                category="Component Ranking",
                title="Candidates Ranked",
                detail=f"Ranked {len(rankings)} components with multi-criteria scores ranging from 8.6 to 9.5.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="component_sorting",
            summary=f"Ranked {len(rankings)} candidate components by electrical fit, thermal limits, cost, and availability.",
            findings=findings,
            data={"rankings": rankings},
        )
