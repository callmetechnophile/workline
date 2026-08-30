"""
SurrealDB repository for change requests, artifact versions, and approvals (Sections 9, 10, 61, 62).
"""

from typing import Any, Dict, List, Optional
from loguru import logger
from research_agents.engineering_change_control.schemas import (
    ApprovalObject,
    ArtifactVersion,
    ChangePlan,
    ChangeRequest,
    ImpactObject,
    RiskObject,
)
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient


class ChangeControlRepository:
    """SurrealDB graph access repository for engineering change control."""

    def __init__(self, db_client: Optional[SurrealDBClient] = None):
        self.db = db_client or SurrealDBClient()
        self._memory_changes: Dict[str, ChangeRequest] = {}
        self._memory_versions: Dict[str, List[ArtifactVersion]] = {}
        self._memory_approvals: Dict[str, ApprovalObject] = {}

    async def create_change(self, change: ChangeRequest) -> ChangeRequest:
        try:
            await self.db.create_node("change_request", change.change_id, change.model_dump())
            await self.db.relate_nodes(f"project:{change.project_id}", "has_change_request", f"change_request:{change.change_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_change fallback to memory: {e}")

        self._memory_changes[change.change_id] = change
        return change

    async def update_change_status(self, change_id: str, new_status: str) -> Optional[ChangeRequest]:
        if change_id in self._memory_changes:
            self._memory_changes[change_id].status = new_status
            try:
                await self.db.upsert_node("change_request", change_id, {"status": new_status})
            except Exception as e:
                logger.warning(f"SurrealDB update status fallback: {e}")
            return self._memory_changes[change_id]
        return None

    async def create_version(self, version: ArtifactVersion) -> ArtifactVersion:
        try:
            await self.db.create_node("artifact_version", version.version_id, version.model_dump())
            if version.supersedes:
                await self.db.relate_nodes(f"artifact_version:{version.version_id}", "supersedes", f"artifact_version:{version.supersedes}")
        except Exception as e:
            logger.warning(f"SurrealDB create_version fallback: {e}")

        if version.artifact_id not in self._memory_versions:
            self._memory_versions[version.artifact_id] = []
        self._memory_versions[version.artifact_id].append(version)
        return version

    async def create_approval(self, approval: ApprovalObject) -> ApprovalObject:
        try:
            await self.db.create_node("approval", approval.approval_id, approval.model_dump())
            await self.db.relate_nodes(f"change_request:{approval.change_id}", "has_approval", f"approval:{approval.approval_id}")
        except Exception as e:
            logger.warning(f"SurrealDB create_approval fallback: {e}")

        self._memory_approvals[approval.approval_id] = approval
        return approval

    async def get_change(self, change_id: str) -> Optional[ChangeRequest]:
        return self._memory_changes.get(change_id)

    async def get_changes(self, project_id: str) -> List[ChangeRequest]:
        return [c for c in self._memory_changes.values() if c.project_id == project_id]

    async def get_artifact_versions(self, artifact_id: str) -> List[ArtifactVersion]:
        return self._memory_versions.get(artifact_id, [])
