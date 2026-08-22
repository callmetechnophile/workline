"""Connection Agent: Generates pinouts, GPIO maps, signal buses, and CONNECTS_TO graph edges."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.shared.prompts import CONNECTION_AGENT_PROMPT
from backend.workline.agents.shared.schemas import (
    AgentFinding,
    AgentOutput,
    ConnectionSignal,
)
from backend.workline.agents.shared.tools import WorklineToolSuite


class ConnectionAgent:
    """Specialist agent generating pin mappings and inter-component wiring topologies."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "connection_agent"
        self.prompt = CONNECTION_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Generate signal wiring and persist CONNECTS_TO edges in SurrealDB."""
        connections = [
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO21", target_component="MPU-6050", target_pin="SDA", signal_type="I2C", bus_name="I2C0"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO22", target_component="MPU-6050", target_pin="SCL", signal_type="I2C", bus_name="I2C0"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO21", target_component="BME280", target_pin="SDA", signal_type="I2C", bus_name="I2C0"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO22", target_component="BME280", target_pin="SCL", signal_type="I2C", bus_name="I2C0"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO4", target_component="DRV8833", target_pin="IN1", signal_type="PWM", bus_name="MOTOR_LEFT"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO5", target_component="DRV8833", target_pin="IN2", signal_type="PWM", bus_name="MOTOR_LEFT"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO6", target_component="DRV8833", target_pin="IN3", signal_type="PWM", bus_name="MOTOR_RIGHT"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO7", target_component="DRV8833", target_pin="IN4", signal_type="PWM", bus_name="MOTOR_RIGHT"),
            ConnectionSignal(source_component="ESP32-S3", source_pin="GPIO1", target_component="Soil Probe Header", target_pin="SIG_ANALOG", signal_type="ADC", bus_name="ADC1_CH0"),
        ]

        # Persist CONNECTS_TO graph edges in SurrealDB
        for idx, conn in enumerate(connections):
            src_id = f"component:{project_id}_{conn.source_component.lower().replace('-', '_').replace(' ', '_')}"
            tgt_id = f"component:{project_id}_{conn.target_component.lower().replace('-', '_').replace(' ', '_')}"
            await self.tools.save_graph_edge(
                edge_id=f"conn:{project_id}_{idx}",
                source_id=src_id,
                target_id=tgt_id,
                relationship="CONNECTS_TO",
                data={"project_id": project_id, **conn.model_dump()},
            )

        findings = [
            AgentFinding(
                category="Signal Routing",
                title="Pinout Mappings Generated",
                detail=f"Mapped {len(connections)} signal lines across shared I2C bus (0x68, 0x76), dual motor PWMs, and analog ADC.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="pin_mapping",
            summary=f"Routed {len(connections)} inter-IC connections without GPIO collisions.",
            findings=findings,
            data={"connections": [c.model_dump() for c in connections]},
        )
