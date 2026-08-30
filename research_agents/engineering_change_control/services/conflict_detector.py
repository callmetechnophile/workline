"""
Concurrent change and conflict detection for EngineeringChangeControlAgent (Sections 65–67).
"""

from typing import List, Optional
import uuid
from research_agents.engineering_change_control.schemas import ChangeConflict, ChangeRequest


class ConflictDetector:
    """Detects concurrent or conflicting change requests targeting identical artifacts."""

    def detect_conflicts(
        self,
        active_changes: List[ChangeRequest],
        new_change: ChangeRequest,
    ) -> Optional[ChangeConflict]:
        for existing in active_changes:
            if existing.change_id == new_change.change_id:
                continue

            if (
                existing.status in ("ANALYZING", "PENDING_APPROVAL", "APPROVED", "IMPLEMENTING")
                and existing.target_artifact
                and existing.target_artifact == new_change.target_artifact
            ):
                return ChangeConflict(
                    conflict_id=f"CONF-{uuid.uuid4().hex[:6].upper()}",
                    change_a=existing.change_id,
                    change_b=new_change.change_id,
                    artifact=existing.target_artifact,
                    description=f"Concurrent change requests '{existing.change_id}' and '{new_change.change_id}' both target artifact '{existing.target_artifact}'.",
                    severity="HIGH",
                    resolution_required=True,
                )
        return None
