"""
Workline AI — Centralized Role-Based & Artifact-Level Permission Service.

Enforces:
1. 5-Tier Project Role Hierarchy (OWNER > ADMIN > ENGINEER > RESEARCHER > VIEWER).
2. Project-level action authorization.
3. Fine-grained Artifact-Level permissions:
   - BOM
   - Component
   - Document
   - Datasheet
   - Research Paper / Result
   - Analysis (Thermal, Signal, Power)
   - Wiring Diagram
   - Procurement Data
   - Knowledge Graph
   - Decision
   - Task
   - Agent Execution
   - Team Management
4. Artifact-level overrides per project.
5. Server-side validation with zero client-side trust.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field

from backend.workline.collaboration.teams.models import TeamRole


class ArtifactType(str, Enum):
    """Types of engineering artifacts governed by permissions."""
    BOM = "BOM"
    COMPONENT = "COMPONENT"
    DOCUMENT = "DOCUMENT"
    DATASHEET = "DATASHEET"
    RESEARCH = "RESEARCH"
    ANALYSIS = "ANALYSIS"
    WIRING = "WIRING"
    PROCUREMENT = "PROCUREMENT"
    KNOWLEDGE_GRAPH = "KNOWLEDGE_GRAPH"
    DECISION = "DECISION"
    TASK = "TASK"
    AGENT_RUN = "AGENT_RUN"
    TEAM_MANAGEMENT = "TEAM_MANAGEMENT"


class AccessLevel(str, Enum):
    """Access levels permitted on artifacts."""
    NONE = "NONE"
    VIEW = "VIEW"
    COMMENT = "COMMENT"
    EDIT = "EDIT"
    EXECUTE = "EXECUTE"
    ADMIN = "ADMIN"


class ActionType(str, Enum):
    """Granular action types requested on artifacts."""
    READ = "READ"
    COMMENT = "COMMENT"
    CREATE = "CREATE"
    WRITE = "WRITE"
    EDIT = "EDIT"
    EXECUTE = "EXECUTE"
    APPROVE = "APPROVE"
    DELETE = "DELETE"


# Baseline Capability Matrix for 5-Tier Roles
DEFAULT_ROLE_PERMISSIONS: Dict[TeamRole, Dict[ArtifactType, AccessLevel]] = {
    TeamRole.OWNER: {
        ArtifactType.BOM: AccessLevel.ADMIN,
        ArtifactType.COMPONENT: AccessLevel.ADMIN,
        ArtifactType.DOCUMENT: AccessLevel.ADMIN,
        ArtifactType.DATASHEET: AccessLevel.ADMIN,
        ArtifactType.RESEARCH: AccessLevel.ADMIN,
        ArtifactType.ANALYSIS: AccessLevel.ADMIN,
        ArtifactType.WIRING: AccessLevel.ADMIN,
        ArtifactType.PROCUREMENT: AccessLevel.ADMIN,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.ADMIN,
        ArtifactType.DECISION: AccessLevel.ADMIN,
        ArtifactType.TASK: AccessLevel.ADMIN,
        ArtifactType.AGENT_RUN: AccessLevel.ADMIN,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.ADMIN,
    },
    TeamRole.ADMIN: {
        ArtifactType.BOM: AccessLevel.EDIT,
        ArtifactType.COMPONENT: AccessLevel.EDIT,
        ArtifactType.DOCUMENT: AccessLevel.EDIT,
        ArtifactType.DATASHEET: AccessLevel.EDIT,
        ArtifactType.RESEARCH: AccessLevel.EDIT,
        ArtifactType.ANALYSIS: AccessLevel.EDIT,
        ArtifactType.WIRING: AccessLevel.EDIT,
        ArtifactType.PROCUREMENT: AccessLevel.EDIT,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.EDIT,
        ArtifactType.DECISION: AccessLevel.EDIT,
        ArtifactType.TASK: AccessLevel.ADMIN,
        ArtifactType.AGENT_RUN: AccessLevel.EXECUTE,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.EDIT,
    },
    TeamRole.ENGINEER: {
        ArtifactType.BOM: AccessLevel.EDIT,
        ArtifactType.COMPONENT: AccessLevel.EDIT,
        ArtifactType.DOCUMENT: AccessLevel.EDIT,
        ArtifactType.DATASHEET: AccessLevel.VIEW,
        ArtifactType.RESEARCH: AccessLevel.VIEW,
        ArtifactType.ANALYSIS: AccessLevel.EDIT,
        ArtifactType.WIRING: AccessLevel.EDIT,
        ArtifactType.PROCUREMENT: AccessLevel.VIEW,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.EDIT,
        ArtifactType.DECISION: AccessLevel.EDIT,
        ArtifactType.TASK: AccessLevel.EDIT,
        ArtifactType.AGENT_RUN: AccessLevel.EXECUTE,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.NONE,
    },
    TeamRole.MEMBER: {  # Compatibility alias matching ENGINEER
        ArtifactType.BOM: AccessLevel.EDIT,
        ArtifactType.COMPONENT: AccessLevel.EDIT,
        ArtifactType.DOCUMENT: AccessLevel.EDIT,
        ArtifactType.DATASHEET: AccessLevel.VIEW,
        ArtifactType.RESEARCH: AccessLevel.VIEW,
        ArtifactType.ANALYSIS: AccessLevel.EDIT,
        ArtifactType.WIRING: AccessLevel.EDIT,
        ArtifactType.PROCUREMENT: AccessLevel.VIEW,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.EDIT,
        ArtifactType.DECISION: AccessLevel.EDIT,
        ArtifactType.TASK: AccessLevel.EDIT,
        ArtifactType.AGENT_RUN: AccessLevel.EXECUTE,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.NONE,
    },
    TeamRole.RESEARCHER: {
        ArtifactType.BOM: AccessLevel.VIEW,
        ArtifactType.COMPONENT: AccessLevel.VIEW,
        ArtifactType.DOCUMENT: AccessLevel.EDIT,
        ArtifactType.DATASHEET: AccessLevel.EDIT,
        ArtifactType.RESEARCH: AccessLevel.EDIT,
        ArtifactType.ANALYSIS: AccessLevel.VIEW,
        ArtifactType.WIRING: AccessLevel.VIEW,
        ArtifactType.PROCUREMENT: AccessLevel.VIEW,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.VIEW,
        ArtifactType.DECISION: AccessLevel.COMMENT,
        ArtifactType.TASK: AccessLevel.EDIT,
        ArtifactType.AGENT_RUN: AccessLevel.EXECUTE,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.NONE,
    },
    TeamRole.VIEWER: {
        ArtifactType.BOM: AccessLevel.VIEW,
        ArtifactType.COMPONENT: AccessLevel.VIEW,
        ArtifactType.DOCUMENT: AccessLevel.VIEW,
        ArtifactType.DATASHEET: AccessLevel.VIEW,
        ArtifactType.RESEARCH: AccessLevel.VIEW,
        ArtifactType.ANALYSIS: AccessLevel.VIEW,
        ArtifactType.WIRING: AccessLevel.VIEW,
        ArtifactType.PROCUREMENT: AccessLevel.VIEW,
        ArtifactType.KNOWLEDGE_GRAPH: AccessLevel.VIEW,
        ArtifactType.DECISION: AccessLevel.VIEW,
        ArtifactType.TASK: AccessLevel.VIEW,
        ArtifactType.AGENT_RUN: AccessLevel.NONE,
        ArtifactType.TEAM_MANAGEMENT: AccessLevel.NONE,
    },
}

ACCESS_LEVEL_HIERARCHY: Dict[AccessLevel, int] = {
    AccessLevel.NONE: 0,
    AccessLevel.VIEW: 1,
    AccessLevel.COMMENT: 2,
    AccessLevel.EDIT: 3,
    AccessLevel.EXECUTE: 4,
    AccessLevel.ADMIN: 5,
}


class PermissionService:
    """
    Centralized authorization engine for role checks and artifact-level permissions.
    """

    def __init__(self):
        # (project_id, artifact_type, artifact_id, user_id) -> AccessLevel override
        self._user_overrides: Dict[str, AccessLevel] = {}

    def has_permission(
        self,
        user_role: TeamRole,
        artifact_type: ArtifactType,
        required_level: AccessLevel,
        project_id: Optional[str] = None,
        artifact_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Determines whether a user role or user override satisfies the required access level.
        """
        # 1. Check user-specific override if provided
        if project_id and artifact_id and user_id:
            key = f"{project_id}:{artifact_type.value}:{artifact_id}:{user_id}"
            if key in self._user_overrides:
                override_level = self._user_overrides[key]
                return ACCESS_LEVEL_HIERARCHY.get(override_level, 0) >= ACCESS_LEVEL_HIERARCHY.get(required_level, 0)

        # 2. Fall back to role matrix
        role_matrix = DEFAULT_ROLE_PERMISSIONS.get(user_role, {})
        allowed_level = role_matrix.get(artifact_type, AccessLevel.NONE)

        return ACCESS_LEVEL_HIERARCHY.get(allowed_level, 0) >= ACCESS_LEVEL_HIERARCHY.get(required_level, 0)

    def set_artifact_override(
        self,
        project_id: str,
        artifact_type: ArtifactType,
        artifact_id: str,
        user_id: str,
        level: AccessLevel,
    ) -> None:
        """Configures fine-grained user access override for an artifact."""
        key = f"{project_id}:{artifact_type.value}:{artifact_id}:{user_id}"
        self._user_overrides[key] = level

    def remove_artifact_override(
        self,
        project_id: str,
        artifact_type: ArtifactType,
        artifact_id: str,
        user_id: str,
    ) -> None:
        """Removes custom override."""
        key = f"{project_id}:{artifact_type.value}:{artifact_id}:{user_id}"
        self._user_overrides.pop(key, None)

    def get_user_permissions(self, role: TeamRole) -> Dict[str, str]:
        """Returns map of artifact types to access level names for UI rendering."""
        matrix = DEFAULT_ROLE_PERMISSIONS.get(role, {})
        return {artifact.value: level.value for artifact, level in matrix.items()}

    def can_perform(
        self,
        user_id: str,
        team_id: str,
        artifact_type: ArtifactType,
        action: ActionType,
        project_id: Optional[str] = None,
        artifact_id: Optional[str] = None,
    ) -> bool:
        """High-level check whether a user can perform an action in a team workspace."""
        if not user_id or not team_id:
            return False
        try:
            from backend.workline.collaboration.teams.service import team_service
            mem = team_service.get_member(team_id, user_id)
            if not mem:
                return False

            user_role = mem.role

            # Map ActionType to required AccessLevel
            action_map = {
                ActionType.READ: AccessLevel.VIEW,
                ActionType.COMMENT: AccessLevel.COMMENT,
                ActionType.CREATE: AccessLevel.EDIT,
                ActionType.WRITE: AccessLevel.EDIT,
                ActionType.EDIT: AccessLevel.EDIT,
                ActionType.EXECUTE: AccessLevel.EXECUTE,
                ActionType.APPROVE: AccessLevel.ADMIN,
                ActionType.DELETE: AccessLevel.ADMIN,
            }
            required_level = action_map.get(action, AccessLevel.VIEW)

            return self.has_permission(
                user_role=user_role,
                artifact_type=artifact_type,
                required_level=required_level,
                project_id=project_id,
                artifact_id=artifact_id,
                user_id=user_id,
            )
        except Exception:
            return False


# Global singleton instance
permission_service = PermissionService()
