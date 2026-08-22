"""Timeline Agent: Generates engineering task graphs, milestones, dependencies, and Gantt schedules."""

from typing import Any, Dict, Optional
from backend.workline.agents.shared.prompts import TIMELINE_AGENT_PROMPT
from backend.workline.agents.shared.schemas import (
    AgentFinding,
    AgentOutput,
    TimelineMilestone,
    TimelineOutput,
)
from backend.workline.agents.shared.tools import WorklineToolSuite


class TimelineAgent:
    """Specialist agent generating scheduled milestones and BLOCKS graph edges."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "timeline_agent"
        self.prompt = TIMELINE_AGENT_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Construct milestone dependencies and persist task graph in SurrealDB."""
        m1 = TimelineMilestone(
            id="m1_spec",
            name="Architecture & Specifications",
            stage="requirements_definition",
            duration_days=5,
            dependencies=[],
            tasks=["Problem specification", "Component candidates identification"],
        )
        m2 = TimelineMilestone(
            id="m2_schematic",
            name="Schematic Design & Power Modeling",
            stage="schematic_capture",
            duration_days=10,
            dependencies=["m1_spec"],
            tasks=["Pin mapping", "Power architecture design", "Driver circuit capture"],
        )
        m3 = TimelineMilestone(
            id="m3_pcb",
            name="PCB Layout & Design Rule Checks",
            stage="pcb_layout",
            duration_days=12,
            dependencies=["m2_schematic"],
            tasks=["Component placement", "Routing power & signal traces", "DRC validation"],
        )
        m4 = TimelineMilestone(
            id="m4_firmware",
            name="Firmware Bring-Up & Validation",
            stage="firmware_architecture",
            duration_days=8,
            dependencies=["m2_schematic"],
            tasks=["HAL initialization", "FreeRTOS task setup", "Sensor calibration loop"],
        )
        m5 = TimelineMilestone(
            id="m5_integration",
            name="Final System Integration & BOM Compilation",
            stage="system_integration",
            duration_days=5,
            dependencies=["m3_pcb", "m4_firmware"],
            tasks=["BOM compilation", "End-to-end electrical test", "Field testing"],
        )

        milestones = [m1, m2, m3, m4, m5]
        task_graph = [m.model_dump() for m in milestones]

        timeline_payload = TimelineOutput(
            task_graph=task_graph,
            milestones=milestones,
            estimated_duration_weeks=6,
            critical_path=["m1_spec", "m2_schematic", "m3_pcb", "m5_integration"],
        )

        # Persist milestone graph nodes and BLOCKS edges into SurrealDB
        for m in milestones:
            await self.tools.save_graph_node(
                node_id=f"milestone:{project_id}_{m.id}",
                node_type="Milestone",
                label=m.name,
                data=m.model_dump(),
            )
            for dep in m.dependencies:
                await self.tools.save_graph_edge(
                    edge_id=f"blocks:{dep}_{m.id}",
                    source_id=f"milestone:{project_id}_{dep}",
                    target_id=f"milestone:{project_id}_{m.id}",
                    relationship="BLOCKS",
                )

        findings = [
            AgentFinding(
                category="Schedule",
                title="Task Graph Generated",
                detail=f"Constructed 5 sequential engineering milestones with 6-week estimated duration.",
                severity="INFO",
            )
        ]

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="project_planning",
            summary="Constructed 5 engineering milestones, critical path, and dependency graph.",
            findings=findings,
            data=timeline_payload.model_dump(),
        )
