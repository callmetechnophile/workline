"""Project, version, and workspace bundle repository for SurrealDB."""

import json
from typing import Any, Dict, List, Optional
from backend.workline.database.models import (
    ProjectModel,
    ProjectVersionModel,
    WorkspaceBundleModel,
)
from backend.workline.database.surrealdb import SurrealDBManager, surreal_db


class ProjectRepository:
    """Repository handling project persistence, version history, and bundles in SurrealDB."""

    def __init__(self, db: SurrealDBManager = surreal_db):
        self.db = db
        # In-memory storage cache to ensure local testability & offline persistence
        self._memory_projects: Dict[str, ProjectModel] = {}
        self._memory_versions: Dict[str, List[ProjectVersionModel]] = {}
        self._memory_bundles: Dict[str, WorkspaceBundleModel] = {}

    async def create_project(self, project: ProjectModel) -> ProjectModel:
        """Create a new project record."""
        p_id = project.id or f"project:{project.name}"
        project.id = p_id

        # Update in-memory fallback
        self._memory_projects[p_id] = project
        self._memory_projects[project.name] = project

        if await self.db.is_connected():
            try:
                data = project.model_dump()
                sql = f"CREATE {p_id} CONTENT $data;"
                await self.db.query(sql, {"data": data})
            except Exception:
                pass

        return project

    async def get_project(self, project_id: str) -> Optional[ProjectModel]:
        """Fetch project by canonical ID or name."""
        if not project_id.startswith("project:"):
            target_id = f"project:{project_id}"
        else:
            target_id = project_id

        if await self.db.is_connected():
            try:
                sql = f"SELECT * FROM {target_id};"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    item = res[0]
                    if isinstance(item, dict) and "result" in item:
                        item = item["result"]
                    if isinstance(item, list) and len(item) > 0:
                        return ProjectModel.model_validate(item[0])
                    elif isinstance(item, dict):
                        return ProjectModel.model_validate(item)
            except Exception:
                pass

        return self._memory_projects.get(target_id) or self._memory_projects.get(project_id)

    async def list_projects(self) -> List[ProjectModel]:
        """List all saved projects."""
        if await self.db.is_connected():
            try:
                sql = "SELECT * FROM projects;"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    items = res[0]
                    if isinstance(items, dict) and "result" in items:
                        items = items["result"]
                    if isinstance(items, list):
                        return [ProjectModel.model_validate(p) for p in items]
            except Exception:
                pass

        # Return unique in-memory projects
        seen = set()
        unique = []
        for p in self._memory_projects.values():
            if p.id and p.id not in seen:
                seen.add(p.id)
                unique.append(p)
        return unique

    async def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[ProjectModel]:
        """Update existing project fields."""
        p = await self.get_project(project_id)
        if not p:
            return None

        p_data = p.model_dump()
        p_data.update(updates)
        updated_model = ProjectModel.model_validate(p_data)

        self._memory_projects[p.id] = updated_model
        self._memory_projects[p.name] = updated_model

        if await self.db.is_connected():
            try:
                sql = f"UPDATE {p.id} MERGE $updates;"
                await self.db.query(sql, {"updates": updates})
            except Exception:
                pass

        return updated_model

    async def delete_project(self, project_id: str) -> bool:
        """Delete project from store."""
        target_id = project_id if project_id.startswith("project:") else f"project:{project_id}"
        found = target_id in self._memory_projects or project_id in self._memory_projects

        self._memory_projects.pop(target_id, None)
        self._memory_projects.pop(project_id, None)

        if await self.db.is_connected():
            try:
                sql = f"DELETE {target_id};"
                await self.db.query(sql)
                return True
            except Exception:
                pass

        return found

    async def save_version(self, version: ProjectVersionModel) -> ProjectVersionModel:
        """Record an immutable version snapshot."""
        v_id = version.id or f"project_version:{version.project_id}_{version.version_num}"
        version.id = v_id

        if version.project_id not in self._memory_versions:
            self._memory_versions[version.project_id] = []
        self._memory_versions[version.project_id].append(version)

        if await self.db.is_connected():
            try:
                sql = f"CREATE {v_id} CONTENT $data;"
                await self.db.query(sql, {"data": version.model_dump()})
            except Exception:
                pass

        return version

    async def get_versions(self, project_id: str) -> List[ProjectVersionModel]:
        """Retrieve version history for a project."""
        if await self.db.is_connected():
            try:
                sql = f"SELECT * FROM project_versions WHERE project_id = '{project_id}' ORDER BY version_num ASC;"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    items = res[0]
                    if isinstance(items, dict) and "result" in items:
                        items = items["result"]
                    if isinstance(items, list):
                        return [ProjectVersionModel.model_validate(v) for v in items]
            except Exception:
                pass

        return self._memory_versions.get(project_id, [])

    async def save_bundle(self, bundle: WorkspaceBundleModel) -> WorkspaceBundleModel:
        """Save a compressed workspace bundle."""
        b_id = bundle.id or f"workspace_bundle:{bundle.name}_{bundle.checksum[:8]}"
        bundle.id = b_id

        self._memory_bundles[b_id] = bundle

        if await self.db.is_connected():
            try:
                sql = f"CREATE {b_id} CONTENT $data;"
                await self.db.query(sql, {"data": bundle.model_dump()})
            except Exception:
                pass

        return bundle

    async def get_bundles(self, user_id: Optional[str] = None) -> List[WorkspaceBundleModel]:
        """List saved bundles."""
        if await self.db.is_connected():
            try:
                sql = "SELECT * FROM workspace_bundles ORDER BY saved_at DESC;"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    items = res[0]
                    if isinstance(items, dict) and "result" in items:
                        items = items["result"]
                    if isinstance(items, list):
                        return [WorkspaceBundleModel.model_validate(b) for b in items]
            except Exception:
                pass

        bundles = list(self._memory_bundles.values())
        if user_id:
            bundles = [b for b in bundles if b.user_id == user_id]
        return bundles

    async def get_bundle(self, bundle_id: str) -> Optional[WorkspaceBundleModel]:
        """Retrieve bundle by ID."""
        target_id = bundle_id if bundle_id.startswith("workspace_bundle:") else f"workspace_bundle:{bundle_id}"

        if await self.db.is_connected():
            try:
                sql = f"SELECT * FROM {target_id};"
                res = await self.db.query(sql)
                if res and isinstance(res, list) and len(res) > 0:
                    item = res[0]
                    if isinstance(item, dict) and "result" in item:
                        item = item["result"]
                    if isinstance(item, list) and len(item) > 0:
                        return WorkspaceBundleModel.model_validate(item[0])
                    elif isinstance(item, dict):
                        return WorkspaceBundleModel.model_validate(item)
            except Exception:
                pass

        return self._memory_bundles.get(target_id) or self._memory_bundles.get(bundle_id)
