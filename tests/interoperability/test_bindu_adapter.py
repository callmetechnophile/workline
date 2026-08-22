"""Tests for Bindu A2A Client, Server, and Adapter."""

import pytest
from backend.workline.interoperability.bindu.adapter import BinduAdapter
from backend.workline.interoperability.bindu.client import BinduClient
from backend.workline.interoperability.bindu.messaging import BinduMessageEnvelope
from backend.workline.interoperability.bindu.server import BinduServer


@pytest.mark.asyncio
async def test_bindu_client_task_execution():
    client = BinduClient()
    agent = await client.discover_agent("ThermalSolver")
    assert agent is not None
    assert agent.name == "ThermalSolver"

    caps = await client.get_capabilities("ThermalSolver")
    assert any(c.capability_id == "thermal_simulation" for c in caps)

    result = await client.send_task(
        agent_id="ThermalSolver",
        capability="thermal_simulation",
        payload={
            "board_width": 100.0,
            "board_height": 80.0,
            "ambient_temp": 25.0,
            "components": [
                {"name": "U1", "power_dissipation_watts": 1.5},
                {"name": "R1", "power_dissipation_watts": 0.2},
            ],
        },
        task_id="TASK-BINDU-01",
    )

    assert result["status"] == "COMPLETED"
    assert "max_temperature" in result
    assert result["max_temperature"] > 25.0


@pytest.mark.asyncio
async def test_bindu_server_roundtrip():
    server = BinduServer()

    # Query exported capabilities
    env = BinduMessageEnvelope(
        sender_id="peer-agent-01",
        recipient_id=server.server_id,
        action="CAPABILITIES",
    )

    res_env = await server.receive_task(env)
    assert res_env.action == "RESULT"
    assert "component_lookup" in res_env.payload.get("capabilities", {})

    # Execute capability
    task_env = BinduMessageEnvelope(
        sender_id="peer-agent-01",
        recipient_id=server.server_id,
        action="SUBMIT_TASK",
        payload={"capability": "component_lookup", "parameters": {"mpn": "STM32F405RGT6"}},
    )

    task_res = await server.receive_task(task_env)
    assert task_res.payload["status"] == "COMPLETED"
    assert task_res.payload["category"] == "Microcontroller"


@pytest.mark.asyncio
async def test_bindu_adapter_cancellation():
    adapter = BinduAdapter()
    agents = await adapter.discover()
    assert len(agents) >= 2

    # Test cancel
    task_id = "TASK-CANCEL-01"
    # Submit and cancel
    await adapter.client.send_task("CodeReviewAgent", "code_review", {"code": "int main() { while(1); }"}, task_id)
    cancelled = await adapter.cancel(task_id)
    assert cancelled is True
