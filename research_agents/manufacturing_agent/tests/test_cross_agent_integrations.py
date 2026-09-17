"""Tests for Cross-Agent Integrations (Agents #14, #16, #18, #21, #22, #23, #25)."""
import pytest
from research_agents.manufacturing_agent.agent import ManufacturingDFMAgent
from research_agents.manufacturing_agent.schemas import ManufacturingAgentInput

@pytest.mark.asyncio
async def test_cross_agent_handoffs_lifecycle():
    agent = ManufacturingDFMAgent()
    inp = ManufacturingAgentInput(
        project_id="PROJ-CROSS-01",
        components=[{
            "component_id": "HOUSING",
            "intended_process": "CNC_MACHINING",
            "material": "ALUMINUM_6061",
            "pocket_depth_mm": 40.0,
            "pocket_corner_radius_mm": 5.0,
        }],
        assemblies=[{
            "assembly_id": "MAIN_ASSY",
            "part_count": 6,
            "fastener_count": 12,
            "orientation_ambiguity": True,
        }],
    )
    out = await agent.run(inp)
    assert out.status == "success"
    assert len(out.cost_drivers) >= 1
    assert len(out.inspections) >= 1
    assert len(out.recommendations) >= 1
    assert out.readiness is not None
