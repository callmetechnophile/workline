"""Unit tests for the 10 specialist builder agents and Builder Orchestrator."""

import asyncio
import pytest
from backend.workline.agents.builder.bom_agent import BOMAgent
from backend.workline.agents.builder.builder_agent import BuilderAgent
from backend.workline.agents.builder.component_agent import ComponentAgent
from backend.workline.agents.builder.connection_agent import ConnectionAgent
from backend.workline.agents.builder.finance_agent import FinanceAgent
from backend.workline.agents.builder.firmware_agent import FirmwareAgent
from backend.workline.agents.builder.listing_agent import ListingAgent
from backend.workline.agents.builder.pcb_agent import PCBAgent
from backend.workline.agents.builder.power_agent import PowerAgent
from backend.workline.agents.builder.sorting_agent import SortingAgent
from backend.workline.agents.builder.validation_agent import ValidationAgent
from backend.workline.agents.shared.tools import WorklineToolSuite


def test_listing_and_sorting_agents():
    """Test candidate component discovery and multi-criteria ranking."""
    async def _run():
        tools = WorklineToolSuite()
        listing = ListingAgent(tools)
        sorting = SortingAgent(tools)

        ctx = {"task": "Find hardware for rover"}
        l_out = await listing.execute("test_p", ctx)
        assert l_out.status == "COMPLETED"
        assert len(l_out.data["candidates"]) >= 4

        s_out = await sorting.execute("test_p", ctx)
        assert s_out.status == "COMPLETED"
        assert len(s_out.data["rankings"]) >= 4

    asyncio.run(_run())


def test_component_and_connection_agents():
    """Test electrical limit validation (with UNKNOWN support) and GPIO signal mapping."""
    async def _run():
        tools = WorklineToolSuite()
        comp = ComponentAgent(tools)
        conn = ConnectionAgent(tools)

        ctx = {"task": "Verify components and map signals"}
        comp_out = await comp.execute("test_p", ctx)
        assert comp_out.status == "COMPLETED"
        assert any(v["status"] == "UNKNOWN" for v in comp_out.data["validations"])
        assert any(v["status"] == "VALIDATED" for v in comp_out.data["validations"])

        conn_out = await conn.execute("test_p", ctx)
        assert conn_out.status == "COMPLETED"
        assert len(conn_out.data["connections"]) >= 5

    asyncio.run(_run())


def test_power_firmware_and_pcb_agents():
    """Test power budgeting, FreeRTOS task specs, and PCB rules (PINN: NOT_IMPLEMENTED)."""
    async def _run():
        tools = WorklineToolSuite()
        pwr = PowerAgent(tools)
        fw = FirmwareAgent(tools)
        pcb = PCBAgent(tools)

        ctx = {"task": "Model power and layout"}
        pwr_out = await pwr.execute("test_p", ctx)
        assert pwr_out.status == "COMPLETED"
        assert len(pwr_out.data["rails"]) == 2

        fw_out = await fw.execute("test_p", ctx)
        assert fw_out.status == "COMPLETED"
        assert len(fw_out.data["tasks"]) >= 4

        pcb_out = await pcb.execute("test_p", ctx)
        assert pcb_out.status == "COMPLETED"
        assert pcb_out.data["physics_simulation_status"] in ("NOT_IMPLEMENTED", "PINN_TRAINED_AND_OPTIMIZED")

    asyncio.run(_run())


def test_validation_bom_and_builder_orchestrator():
    """Test multi-stage validation, authoritative BOM compilation, and Builder Orchestrator."""
    async def _run():
        tools = WorklineToolSuite()
        builder = BuilderAgent(tools)

        ctx = {"task": "Build rover hardware sub-tree", "project": {"name": "test_rover"}}
        b_out = await builder.execute("test_rover", ctx)

        assert b_out.agent == "builder_agent"
        assert b_out.status == "COMPLETED"
        assert b_out.stage == "hardware_build_complete"
        assert "bom" in b_out.data
        assert b_out.data["bom"]["item_count"] >= 8
        assert b_out.data["bom"]["total_estimated_cost_usd"] > 0.0

    asyncio.run(_run())
