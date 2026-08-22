"""Firmware Agent: Generates firmware architecture, RTOS task specs, priorities, and HAL drivers."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.shared.prompts import FIRMWARE_AGENT_PROMPT
from backend.workline.agents.shared.schemas import (
    AgentFinding,
    AgentOutput,
    FirmwareArchitecture,
    FirmwareTask,
)
from backend.workline.agents.shared.tools import WorklineToolSuite


class FirmwareAgent:
    """Specialist agent defining embedded firmware architecture, RTOS tasks, and driver specifications."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "firmware_agent"
        self.prompt = FIRMWARE_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Produce firmware architectural blueprint."""
        tasks = [
            FirmwareTask(name="task_motor_control", priority=4, rate_hz=100.0, description="PID speed and directional PWM update loop"),
            FirmwareTask(name="task_imu_fusion", priority=3, rate_hz=50.0, description="Read MPU-6050 FIFO and compute attitude quaternion"),
            FirmwareTask(name="task_environmental", priority=1, rate_hz=1.0, description="Poll BME280 temperature, humidity, and soil probe ADC"),
            FirmwareTask(name="task_telemetry_wifi", priority=2, rate_hz=2.0, description="Publish MQTT JSON payload over Wi-Fi / ESP-NOW"),
            FirmwareTask(name="task_power_watchdog", priority=5, rate_hz=10.0, description="Monitor battery voltage and trigger low-power safe state"),
        ]

        fw_arch = FirmwareArchitecture(
            framework="ESP-IDF v5.2 / FreeRTOS SMP",
            hal_drivers=[
                "esp_driver_i2c (Master mode @ 400kHz)",
                "esp_driver_ledc (PWM for DRV8833 H-bridge)",
                "esp_driver_adc (Continuous ADC calibration mode)",
                "esp_wifi & esp_now (Telemetry stack)",
            ],
            tasks=tasks,
            communication_protocols=["I2C", "LEDC-PWM", "MQTT / ESP-NOW", "UART0-Console"],
        )

        findings = [
            AgentFinding(
                category="Firmware Architecture",
                title="FreeRTOS Task Scheduling Designed",
                detail=f"Constructed {len(tasks)} prioritized real-time tasks with hardware watchdog supervisor.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="firmware_architecture",
            summary=f"Defined ESP-IDF / FreeRTOS firmware architecture with {len(tasks)} real-time tasks and HAL drivers.",
            findings=findings,
            data=fw_arch.model_dump(),
        )
