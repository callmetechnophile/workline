import pytest
from research_agents.hardware_thermal_agent import HardwareThermalAgent
from research_agents.hardware_thermal_agent.agent import HardwareThermalInput
from armourflow.registry import AuthoritativeAgentRegistry


def test_agent_23_manifest_resolution():
    registry = AuthoritativeAgentRegistry()
    manifest = registry.get_agent("agent.23")
    assert manifest is not None
    assert manifest.name == "HardwareThermalAgent"
    assert manifest.entrypoint == "research_agents.hardware_thermal_agent.agent:HardwareThermalAgent"
    assert "hardware.thermal" in manifest.capabilities


@pytest.mark.asyncio
async def test_hardware_thermal_agent_execution():
    agent = HardwareThermalAgent()
    input_data = HardwareThermalInput(
        project_id="proj-test-thermal",
        board_dimensions_mm={"width": 120.0, "height": 90.0, "layers": 4},
        enclosure_ambient_temp_c=30.0,
        components=[
            {"mpn": "USB5734/MR", "power_w": 1.2, "theta_ja_c_w": 28.0, "x": 10.0, "y": 20.0},
            {"mpn": "TPS65987DDHR", "power_w": 0.8, "theta_ja_c_w": 35.0, "x": 40.0, "y": 50.0},
        ]
    )

    output = await agent.run(input_data)
    assert output.status == "SUCCESS"
    assert output.project_id == "proj-test-thermal"
    assert len(output.stackup_recommendation) == 4
    assert len(output.hotspots) == 2
    assert output.compliance_verdict in ("PASS", "MARGINAL_REVIEW")
