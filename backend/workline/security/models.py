"""
Role-Based Access Control (RBAC) & Governance Action Tiers.
"""

from enum import Enum
from typing import List, Set
from pydantic import BaseModel, Field


class Role(str, Enum):
    ADMIN = "ADMIN"
    ENGINEER = "ENGINEER"
    REVIEWER = "REVIEWER"
    PROCUREMENT = "PROCUREMENT"
    AGENT = "AGENT"


class ActionTier(str, Enum):
    """3-Tier Separation of Autonomous vs. Human-Governed Actions."""
    RECOMMENDATION = "RECOMMENDATION"         # Autonomous read/analysis, no physical changes
    AUTHORIZED_ACTION = "AUTHORIZED_ACTION"   # Human reviewer/engineer has signed off
    EXECUTED_ACTION = "EXECUTED_ACTION"       # State change or financial commitment applied


class Permission(str, Enum):
    READ_PROJECT = "project:read"
    WRITE_PROJECT = "project:write"
    RUN_SIMULATION = "simulation:run"
    SUBMIT_BOM = "bom:submit"
    APPROVE_BOM = "bom:approve"
    ORDER_EXECUTE = "order:execute"
    MANAGE_ROLES = "roles:manage"


# Default Role-to-Permissions Mapping
ROLE_PERMISSIONS: dict[Role, Set[Permission]] = {
    Role.ADMIN: set(Permission),
    Role.ENGINEER: {
        Permission.READ_PROJECT,
        Permission.WRITE_PROJECT,
        Permission.RUN_SIMULATION,
        Permission.SUBMIT_BOM,
    },
    Role.REVIEWER: {
        Permission.READ_PROJECT,
        Permission.APPROVE_BOM,
    },
    Role.PROCUREMENT: {
        Permission.READ_PROJECT,
        Permission.APPROVE_BOM,
        Permission.ORDER_EXECUTE,
    },
    Role.AGENT: {
        Permission.READ_PROJECT,
        Permission.WRITE_PROJECT,
        Permission.RUN_SIMULATION,
        # Agents CANNOT execute orders or approve BOMs autonomously without human authorization
    },
}


class SecurityContext(BaseModel):
    """User/Principal identity and active role session."""
    user_id: str
    role: Role
    permissions: List[Permission] = Field(default_factory=list)

    def has_permission(self, perm: Permission) -> bool:
        if perm in self.permissions:
            return True
        return perm in ROLE_PERMISSIONS.get(self.role, set())
