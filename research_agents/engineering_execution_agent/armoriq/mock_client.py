"""
Test-only mock ArmorIQ client for isolated testing (Section 67).
Simulates cryptographic delegation, plan capture, invocations, scope denials, expired authority, and receipts.
MUST NEVER BE USED IN PRODUCTION MODE.
"""

import time
from typing import Any, Callable, Dict, List, Optional
import uuid
from backend.armoriq.policies import ScopeViolationError


class MockArmorIQClient:
    """Test-only mock implementation of ArmorIQ client."""

    def __init__(
        self,
        agent_name: str = "EngineeringExecutionAgent",
        should_fail_invoke: bool = False,
        simulate_unavailable: bool = False,
    ):
        self.agent_name = agent_name
        self.should_fail_invoke = should_fail_invoke
        self.simulate_unavailable = simulate_unavailable
        self.captured_plans: List[Dict[str, Any]] = []
        self.delegations: List[Dict[str, Any]] = []
        self.invocations: List[Dict[str, Any]] = []

    def capture_plan(self, user_intent: str) -> Dict[str, Any]:
        if self.simulate_unavailable:
            raise RuntimeError("ArmorIQ authorization layer unavailable.")

        receipt_id = f"MOCK-PLAN-RCPT-{uuid.uuid4().hex[:8]}"
        receipt = {
            "receipt_id": receipt_id,
            "timestamp": time.time(),
            "agent": "Planner Agent",
            "scope": ["delegate", "filesystem", "shell", "test_runner"],
            "parent_receipt_id": None,
            "user_intent": user_intent,
            "signature": f"sig_mock_{uuid.uuid4().hex[:12]}",
        }
        self.captured_plans.append(receipt)
        return receipt

    def delegate(
        self,
        child_agent_id: str,
        requested_scope: List[str],
        parent_receipt: Dict[str, Any],
        parent_agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.simulate_unavailable:
            raise RuntimeError("ArmorIQ authorization layer unavailable.")

        receipt_id = f"MOCK-DEL-RCPT-{uuid.uuid4().hex[:8]}"
        receipt = {
            "receipt_id": receipt_id,
            "timestamp": time.time(),
            "agent": child_agent_id,
            "scope": requested_scope,
            "parent_receipt_id": parent_receipt.get("receipt_id") if parent_receipt else None,
            "signature": f"sig_mock_{uuid.uuid4().hex[:12]}",
        }
        self.delegations.append(receipt)
        return receipt

    def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        receipt_dict: Dict[str, Any],
        tool_callable: Optional[Callable[..., Any]] = None,
        agent_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        if self.simulate_unavailable:
            raise RuntimeError("ArmorIQ authorization layer unavailable.")

        if self.should_fail_invoke:
            raise ScopeViolationError(
                agent=agent_override or self.agent_name,
                tool=tool_name,
                allowed_scope=receipt_dict.get("scope", []),
                details="Mock forced scope violation.",
            )

        # Verify scope
        allowed_scope = receipt_dict.get("scope", [])
        if tool_name not in allowed_scope and not any(tool_name.startswith(f"{s}.") for s in allowed_scope):
            raise ScopeViolationError(
                agent=agent_override or self.agent_name,
                tool=tool_name,
                allowed_scope=allowed_scope,
                details=f"Mock: Tool '{tool_name}' is not in delegated scope.",
            )

        result = {}
        if tool_callable is not None:
            result = tool_callable(**args)

        receipt_id = f"MOCK-INVOKE-RCPT-{uuid.uuid4().hex[:8]}"
        record = {
            "status": "success",
            "result": result,
            "receipt": {
                "receipt_id": receipt_id,
                "tool": tool_name,
                "timestamp": time.time(),
                "status": "SUCCESS",
            },
            "receipt_id": receipt_id,
        }
        self.invocations.append(record)
        return record

    def verify_receipt_signature(self, receipt_dict: Dict[str, Any]) -> bool:
        return bool(receipt_dict and receipt_dict.get("signature"))
