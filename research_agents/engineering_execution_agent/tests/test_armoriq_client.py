"""
Unit tests for ArmorIQ client integration and cryptographic delegation (Sections 3, 17, 18, 20, 67).
"""

from research_agents.engineering_execution_agent.armoriq.client import ArmorIQClient
from research_agents.engineering_execution_agent.armoriq.mock_client import MockArmorIQClient


def test_armoriq_client_capture_plan_and_delegate():
    client = ArmorIQClient()

    # 1. Capture Plan
    plan_receipt = client.capture_plan("Implement avionics firmware and sensor drivers")
    assert plan_receipt is not None
    assert "receipt_id" in plan_receipt
    assert plan_receipt.get("agent") == "Planner Agent"

    # 2. Delegate to EngineeringExecutionAgent
    child_receipt = client.delegate(
        child_agent_id="EngineeringExecutionAgent",
        requested_scope=["filesystem", "shell", "test_runner"],
        parent_receipt=plan_receipt,
    )
    assert child_receipt is not None
    assert child_receipt.get("agent") == "EngineeringExecutionAgent"
    assert "filesystem" in child_receipt.get("scope", [])


def test_armoriq_client_invoke_with_receipt():
    client = ArmorIQClient()
    plan_receipt = client.capture_plan("Test tool execution")
    child_receipt = client.delegate(
        child_agent_id="EngineeringExecutionAgent",
        requested_scope=["filesystem", "filesystem.read"],
        parent_receipt=plan_receipt,
    )

    def dummy_read(path: str = "test.txt"):
        return f"content of {path}"

    result = client.invoke(
        tool_name="filesystem",
        args={"path": "sensor.py"},
        receipt_dict=child_receipt,
        tool_callable=dummy_read,
    )

    assert result["status"] == "success"
    assert "sensor.py" in str(result["result"])
    assert result.get("receipt_id") is not None


def test_mock_armoriq_client_full_lifecycle():
    mock = MockArmorIQClient()
    plan = mock.capture_plan("Mock Plan")
    del_rcpt = mock.delegate("EngineeringExecutionAgent", ["filesystem", "shell"], plan)

    res = mock.invoke(
        tool_name="filesystem",
        args={},
        receipt_dict=del_rcpt,
        tool_callable=lambda: "mocked file created",
    )
    assert res["status"] == "success"
    assert res["result"] == "mocked file created"
