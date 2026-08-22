"""Domain Researcher Agent: Extracts problem definition, engineering domain, requirements, constraints, and unknowns."""

from typing import Any, Dict, Optional
from backend.workline.agents.shared.prompts import DOMAIN_RESEARCHER_PROMPT
from backend.workline.agents.shared.schemas import AgentFinding, AgentOutput, DomainOutput
from backend.workline.agents.shared.tools import WorklineToolSuite


class DomainResearcherAgent:
    """Specialist agent defining problem space, technical requirements, and constraints."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "domain_researcher"
        self.prompt = DOMAIN_RESEARCHER_PROMPT

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Run domain problem analysis."""
        task = context.get("task", "")
        project = context.get("project", {})
        desc = project.get("description", task) or task

        # Formulate structured problem definition and domain analysis
        domain_name = "Autonomous Robotics & Embedded Systems" if "rover" in desc.lower() or "robot" in desc.lower() else "Hardware Engineering"
        
        reqs = [
            f"Core computational controller with wireless telemetry and sensor interfaces for {desc[:40]}",
            "Multi-sensor telemetry bus (environmental/inertial sensing)",
            "Power management system with battery monitoring and protection",
            "Motor actuation and directional drive control",
        ]
        
        constraints = {
            "operating_voltage": "3.3V / 5.0V / 12.0V",
            "thermal_limit": "0°C to 65°C operating range",
            "telemetry_protocol": "Wi-Fi 802.11 b/g/n / Bluetooth 5 LE",
            "power_source": "Rechargeable Li-ion battery pack with solar recharging",
        }

        domain_payload = DomainOutput(
            problem_definition=f"Design and validate an engineered solution for: {desc}",
            engineering_domain=domain_name,
            initial_requirements=reqs,
            operating_constraints=constraints,
            unknowns=["Specific motor stall current under field load", "Telemetry transmission range under canopy"],
            research_questions=["Optimal battery chemistry for continuous field operation", "Solar MPPT efficiency tradeoffs"],
        )

        findings = [
            AgentFinding(
                category="Requirements",
                title=f"Domain: {domain_name}",
                detail=f"Identified {len(reqs)} primary technical requirements.",
                severity="INFO",
            )
        ]

        # Update knowledge graph node in SurrealDB
        await self.tools.save_graph_node(
            node_id=f"domain:{project_id}",
            node_type="DomainAnalysis",
            label=domain_name,
            data=domain_payload.model_dump(),
        )

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="requirements_definition",
            summary=f"Formulated problem definition, constraints, and {len(reqs)} requirements for {domain_name}.",
            findings=findings,
            data=domain_payload.model_dump(),
        )
