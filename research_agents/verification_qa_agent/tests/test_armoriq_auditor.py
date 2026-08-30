"""
Unit tests for ArmorIQAuditor service (Sections 29, 30, 57).
"""

from research_agents.verification_qa_agent.services.armoriq_auditor import ArmorIQAuditor


def test_armoriq_auditor_validates_receipts():
    auditor = ArmorIQAuditor()

    tool_calls = [
        {
            "tool_call_id": "CALL-01",
            "task_id": "TASK-01",
            "tool": "filesystem",
            "operation": "create",
            "resource": "firmware/driver.py",
            "armoriq_receipt_id": "RCPT-01",
        }
    ]

    receipts = [
        {
            "receipt_id": "RCPT-01",
            "agent_name": "EngineeringExecutionAgent",
            "signature": "valid_signature_hash",
        }
    ]

    res = auditor.audit_armoriq_execution(tool_calls, receipts, "AUTH-01")

    assert res["status"] == "PASS"
    assert res["valid_receipts"] == 1
    assert res["missing_receipts"] == 0
