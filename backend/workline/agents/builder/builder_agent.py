"""Builder Agent Orchestrator: Coordinates the hardware engineering sub-tree specialists."""

from typing import Any, Dict, List, Optional
from backend.workline.agents.builder.bom_agent import BOMAgent
from backend.workline.agents.builder.component_agent import ComponentAgent
from backend.workline.agents.builder.connection_agent import ConnectionAgent
from backend.workline.agents.builder.finance_agent import FinanceAgent
from backend.workline.agents.builder.firmware_agent import FirmwareAgent
from backend.workline.agents.builder.listing_agent import ListingAgent
from backend.workline.agents.builder.pcb_agent import PCBAgent
from backend.workline.agents.builder.power_agent import PowerAgent
from backend.workline.agents.builder.sorting_agent import SortingAgent
from backend.workline.agents.builder.validation_agent import ValidationAgent
from backend.workline.agents.shared.prompts import BUILDER_ORCHESTRATOR_PROMPT
from backend.workline.agents.shared.schemas import AgentFinding, AgentOutput
from backend.workline.agents.shared.tools import WorklineToolSuite


class BuilderAgent:
    """Orchestrator for hardware engineering sub-tree execution."""

    def __init__(self, tools: Optional[WorklineToolSuite] = None):
        self.tools = tools or WorklineToolSuite()
        self.name = "builder_agent"
        self.prompt = BUILDER_ORCHESTRATOR_PROMPT

        # Sub-tree specialists
        self.listing_agent = ListingAgent(self.tools)
        self.sorting_agent = SortingAgent(self.tools)
        self.finance_agent = FinanceAgent(self.tools)
        self.component_agent = ComponentAgent(self.tools)
        self.connection_agent = ConnectionAgent(self.tools)
        self.power_agent = PowerAgent(self.tools)
        self.firmware_agent = FirmwareAgent(self.tools)
        self.pcb_agent = PCBAgent(self.tools)
        self.validation_agent = ValidationAgent(self.tools)
        self.bom_agent = BOMAgent(self.tools)

    async def execute(self, project_id: str, context: Dict[str, Any]) -> AgentOutput:
        """Run hardware engineering builder pipeline through specialists."""
        all_findings: List[AgentFinding] = []
        builder_data: Dict[str, Any] = {}

        # 1. Listing
        listing_out = await self.listing_agent.execute(project_id, context)
        all_findings.extend(listing_out.findings)
        builder_data["listing"] = listing_out.data

        # 2. Sorting
        sorting_out = await self.sorting_agent.execute(project_id, context)
        all_findings.extend(sorting_out.findings)
        builder_data["sorting"] = sorting_out.data

        # 3. Finance
        finance_out = await self.finance_agent.execute(project_id, context)
        all_findings.extend(finance_out.findings)
        builder_data["finance"] = finance_out.data

        # 4. Component Validation
        comp_out = await self.component_agent.execute(project_id, context)
        all_findings.extend(comp_out.findings)
        builder_data["components"] = comp_out.data

        # 5. Connection Routing
        conn_out = await self.connection_agent.execute(project_id, context)
        all_findings.extend(conn_out.findings)
        builder_data["connections"] = conn_out.data

        # 6. Power Analysis
        pwr_out = await self.power_agent.execute(project_id, context)
        all_findings.extend(pwr_out.findings)
        builder_data["power"] = pwr_out.data

        # 7. Firmware Architecture
        fw_out = await self.firmware_agent.execute(project_id, context)
        all_findings.extend(fw_out.findings)
        builder_data["firmware"] = fw_out.data

        # 8. PCB Constraints
        pcb_out = await self.pcb_agent.execute(project_id, context)
        all_findings.extend(pcb_out.findings)
        builder_data["pcb"] = pcb_out.data

        # 9. Multi-Stage Validation
        val_out = await self.validation_agent.execute(project_id, context)
        all_findings.extend(val_out.findings)
        builder_data["validation"] = val_out.data

        # 10. BOM Generation
        bom_out = await self.bom_agent.execute(project_id, context)
        all_findings.extend(bom_out.findings)
        builder_data["bom"] = bom_out.data

        # Advance project lifecycle stage in SurrealDB
        await self.tools.update_project_state(project_id, {"lifecycle_stage": "hardware_build_complete"})

        return AgentOutput(
            agent=self.name,
            status="COMPLETED",
            stage="hardware_build_complete",
            summary="Hardware engineering build tree completed: candidate ranking, electrical validation, pin routing, power budgeting, firmware specs, PCB rules, validation, and BOM compilation.",
            findings=all_findings,
            data=builder_data,
        )
