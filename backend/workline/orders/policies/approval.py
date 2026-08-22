"""Role-based human approval policy verification for orders."""

from typing import Optional, Set, Tuple
from backend.workline.orders.models import ApprovalStatus, Order, OrderPolicy


class ApprovalPolicyValidator:
    """Enforces human-in-the-loop authorization rules and role privilege restrictions."""

    AUTHORIZED_APPROVER_ROLES: Set[str] = {"OWNER", "ADMIN", "LEAD_ENGINEER", "HARDWARE_LEAD"}
    AUTHORIZED_CREATOR_ROLES: Set[str] = {"OWNER", "ADMIN", "LEAD_ENGINEER", "HARDWARE_LEAD", "ENGINEER"}

    def can_create_order(self, user_role: str) -> bool:
        """Verify if role has order creation privileges."""
        return user_role.upper() in self.AUTHORIZED_CREATOR_ROLES

    def can_approve_order(self, user_role: str, is_agent: bool = False) -> Tuple[bool, Optional[str]]:
        """
        Verify if actor has approval authority.
        Crucial Rule: Autonomous agents are NEVER permitted to approve orders.
        """
        if is_agent:
            return False, "Autonomous agents cannot approve orders. Explicit human authorization is mandatory."

        if user_role.upper() not in self.AUTHORIZED_APPROVER_ROLES:
            return False, f"Role '{user_role}' lacks order approval authority. Required: {self.AUTHORIZED_APPROVER_ROLES}"

        return True, None

    def can_execute_payment(self, user_role: str, is_agent: bool = False) -> Tuple[bool, Optional[str]]:
        """Verify payment initiation rights."""
        if is_agent:
            return False, "Autonomous agents cannot authorize or execute payments."
        return True, None
