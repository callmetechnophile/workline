"""
History-preserving forward rollback manager for EngineeringChangeControlAgent (Sections 69–71).
"""

from datetime import datetime, timezone
import uuid
from typing import Tuple
from research_agents.engineering_change_control.schemas import ArtifactVersion, RollbackObject


class RollbackManager:
    """Performs controlled rollbacks by generating new forward versions without deleting history."""

    def execute_rollback(
        self,
        artifact_id: str,
        target_version: str,
        current_version: str,
        approved_by: str,
        reason: str = "Rollback to previous validated baseline.",
    ) -> Tuple[RollbackObject, ArtifactVersion]:
        # Generate new version increment
        curr_num = int(current_version.replace("v", "").replace("V", "").split(".")[0])
        new_version_str = f"v{curr_num + 1}.0.0"

        roll_id = f"ROLL-{uuid.uuid4().hex[:6].upper()}"
        ver_id = f"VER-{uuid.uuid4().hex[:6].upper()}"

        rollback = RollbackObject(
            rollback_id=roll_id,
            change_id=f"CHANGE-ROLLBACK-{roll_id}",
            target_version=target_version,
            new_version=new_version_str,
            reason=reason,
            approved_by=approved_by,
        )

        new_version = ArtifactVersion(
            version_id=ver_id,
            artifact_id=artifact_id,
            version=new_version_str,
            status="validated",
            created_by=approved_by,
            supersedes=current_version,
        )

        return rollback, new_version
