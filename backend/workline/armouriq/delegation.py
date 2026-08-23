"""
ArmourIQ Delegation Engine: Enforces strict capability subsetting and delegation chain verification.
"""

from typing import Any, Dict, List, Optional, Tuple
from backend.armoriq.receipts import generate_receipt, verify_receipt, CryptographicReceipt
from backend.workline.armouriq.capabilities import AgentCapability, RiskTier
from backend.workline.armouriq.identity import AgentIdentity
from backend.workline.armouriq.trust_context import TrustContext


class DelegationViolationError(Exception):
    """Raised when delegation violates ArmourIQ trust invariants."""
    def __init__(self, message: str, parent_agent: str, child_agent: str, escalated_caps: Optional[List[str]] = None):
        self.parent_agent = parent_agent
        self.child_agent = child_agent
        self.escalated_caps = escalated_caps or []
        super().__init__(f"Delegation Violation ({parent_agent} -> {child_agent}): {message}")


class DelegationManager:
    """Manages verifiable delegation between ADK agents."""

    @classmethod
    def validate_delegation(
        cls,
        parent_context: TrustContext,
        child_identity: AgentIdentity,
        requested_capabilities: Optional[List[AgentCapability]] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates delegation request against ArmourIQ invariants:
        1. Parent must be authenticated.
        2. Project scopes must match exactly (Project Isolation).
        3. CHILD CAPABILITIES ⊆ PARENT CAPABILITIES.
        """
        # 1. Authenticated check
        if not parent_context.is_authenticated:
            return False, "Parent context is not authenticated"

        # 2. Project isolation check
        if parent_context.project_id != child_identity.project_id:
            return False, f"Cross-project delegation denied: parent project '{parent_context.project_id}' != child project '{child_identity.project_id}'"

        # 3. Cryptographic identity check on child
        if not child_identity.verify():
            return False, "Child agent identity verification failed (tampered token or invalid signature)"

        # 4. Capability Subset Invariant: Child cannot exceed parent capabilities
        target_caps = requested_capabilities if requested_capabilities is not None else child_identity.capabilities
        parent_cap_set = set(parent_context.capabilities)
        escalations = [c for c in target_caps if c not in parent_cap_set]

        if escalations:
            return False, f"Capability escalation denied: Child requested {escalations} which are not held by parent {parent_context.agent_id}"

        return True, None

    @classmethod
    def issue_delegation_receipt(
        cls,
        parent_context: TrustContext,
        child_agent_id: str,
        granted_capabilities: List[AgentCapability],
    ) -> CryptographicReceipt:
        """Generates a verifiable cryptographic receipt for the delegation step."""
        scope_strings = [c.value for c in granted_capabilities]
        return generate_receipt(
            agent=child_agent_id,
            scope=scope_strings,
            parent_receipt_id=parent_context.request_id,
            input_data={"parent_agent": parent_context.agent_id, "project_id": parent_context.project_id},
        )
