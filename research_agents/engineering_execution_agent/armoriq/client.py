"""
Production ArmorIQ Client integration for EngineeringExecutionAgent (Sections 3, 4, 17, 18, 20, 65).
Directly interfaces with backend.armoriq cryptographic authority engine.
"""

from typing import Any, Callable, Dict, List, Optional
from loguru import logger

from backend.armoriq.delegation import capture_plan as armoriq_capture_plan
from backend.armoriq.delegation import delegate as armoriq_delegate
from backend.armoriq.policies import ScopeViolationError, validate_tool_invocation
from backend.armoriq.receipts import generate_receipt, save_tool_receipt, verify_receipt


class ArmorIQClient:
    """Production ArmorIQ SDK Client governing execution authority, plan capture, and tool invocation."""

    def __init__(self, agent_name: str = "EngineeringExecutionAgent"):
        self.agent_name = agent_name

    def capture_plan(self, user_intent: str) -> Dict[str, Any]:
        """
        Cryptographically captures root execution plan (Section 20).
        """
        try:
            receipt = armoriq_capture_plan(user_intent)
            return receipt.model_dump()
        except Exception as e:
            logger.error(f"ArmorIQ capture_plan failed: {e}")
            raise

    def delegate(
        self,
        child_agent_id: str,
        requested_scope: List[str],
        parent_receipt: Dict[str, Any],
        parent_agent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Cryptographically delegates scoped execution authority to a child agent (Section 18 & 19).
        """
        p_agent = parent_agent_id or self.agent_name
        try:
            child_receipt = armoriq_delegate(
                agent_name=child_agent_id,
                requested_scope=requested_scope,
                parent_receipt=parent_receipt,
            )
            return child_receipt.model_dump()
        except Exception as e:
            logger.error(f"ArmorIQ delegation from '{p_agent}' to '{child_agent_id}' failed: {e}")
            raise

    def invoke(
        self,
        tool_name: str,
        args: Dict[str, Any],
        receipt_dict: Dict[str, Any],
        tool_callable: Optional[Callable[..., Any]] = None,
        agent_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Validates cryptographic authorization and executes tool invocation (Section 17).
        Never bypasses authorization.
        """
        invoking_agent = agent_override or self.agent_name
        # 1. Cryptographic and policy verification
        validate_tool_invocation(
            agent_name=invoking_agent,
            tool_name=tool_name,
            receipt_dict=receipt_dict,
        )

        # 2. Execute tool callable if provided
        result: Any = {}
        if tool_callable is not None:
            result = tool_callable(**args)

        # 3. Save receipt and record audit trail
        receipt_record = save_tool_receipt(
            agent=invoking_agent,
            parent=receipt_dict.get("parent_receipt_id", "Root"),
            tool=tool_name,
            scope=receipt_dict.get("scope", []),
            status="SUCCESS",
            execution_result=result,
        )

        return {
            "status": "success",
            "result": result,
            "receipt": receipt_record,
            "receipt_id": receipt_record.get("receipt_id") or receipt_dict.get("receipt_id"),
        }

    def verify_receipt_signature(self, receipt_dict: Dict[str, Any]) -> bool:
        """Verifies cryptographic signature integrity."""
        return verify_receipt(receipt_dict)
