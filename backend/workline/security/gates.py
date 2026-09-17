"""
Action governance and authorization gate policies.
"""

from fastapi import HTTPException, status
from loguru import logger

from backend.workline.security.models import ActionTier, Permission, Role, SecurityContext


class GovernancePolicyGate:
    """Enforces boundaries between Agent Recommendations and Executed Actions."""

    @staticmethod
    def enforce_permission(context: SecurityContext, required_perm: Permission):
        """Enforces that the caller holds required permission."""
        if not context.has_permission(required_perm):
            logger.warning(f"[Security] Denied action {required_perm.value} to user {context.user_id} with role {context.role.value}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires permission '{required_perm.value}'. Role '{context.role.value}' is unauthorized.",
            )

    @staticmethod
    def validate_action_tier_transition(current_tier: ActionTier, next_tier: ActionTier, context: SecurityContext):
        """Validates that transitions from RECOMMENDATION to EXECUTED require explicit AUTHORIZED signoff."""
        if next_tier == ActionTier.EXECUTED_ACTION:
            if current_tier != ActionTier.AUTHORIZED_ACTION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot execute an action directly from RECOMMENDATION. Must be AUTHORIZED by a human reviewer first.",
                )
            if context.role == Role.AGENT:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Autonomous agents are forbidden from executing final actions. Human authorization is mandatory.",
                )
