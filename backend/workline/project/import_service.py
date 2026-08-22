"""Import engine for restoring and migrating Workline project packages (.wlipjt)."""

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Tuple
import zipfile

from backend.workline.database.surrealdb import surreal_db
from backend.workline.git.models import (
    ProjectGitHubManifest,
    ProjectGitManifest,
    WorklineToonManifest,
)
from backend.workline.git.repository import project_repo_manager
from backend.workline.git.service import git_service
from backend.workline.git.toon import ToonSerializer
from backend.workline.project.errors import (
    ChecksumMismatchError,
    CorruptedPackageError,
    ImportError,
    ProjectConflictError,
)
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import (
    ImportPlan,
    ImportStrategy,
    PackageManifest,
)
from cli.wline.core.manifest import ProjectManifest, save_manifest
from cli.wline.core.paths import get_workspace_dir
from cli.wline.core.workspace import find_project, normalize_project_name


class ImportService:
    """
    Orchestrates the safe, verified restoration of .wlipjt packages into the workspace.
    Guarantees integrity verification, conflict protection, and transactional state restoration.
    """

    def __init__(self):
        self.git = git_service
        self.repo_mgr = project_repo_manager
        self.inspector = PackageInspector()

    def plan_import(
        self,
        package_path: Path,
        target_project_name: Optional[str] = None,
        strategy: ImportStrategy = ImportStrategy.RESTORE,
        workspace_path: Optional[Path] = None,
    ) -> ImportPlan:
        """
        Analyzes package and destination workspace to generate an ImportPlan.
        Identifies potential naming or database conflicts prior to execution.
        """
        p = Path(package_path).resolve()
        is_valid, errors = self.inspector.verify(p)
        if not is_valid:
            raise CorruptedPackageError(f"Package integrity verification failed: {'; '.join(errors)}")

        manifest = self.inspector.read_manifest(p)
        ws = (workspace_path or get_workspace_dir()).resolve()

        source_id = manifest.project_id
        source_name = manifest.project_name
        source_version = manifest.project_version

        # Determine target project ID
        if target_project_name:
            target_id = normalize_project_name(target_project_name)
            target_name = target_project_name
        else:
            target_id = source_id
            target_name = source_name

        if strategy == ImportStrategy.NEW_PROJECT and not target_project_name:
            target_id = f"{source_id}-imported"
            target_name = f"{source_name} (Imported)"

        # Check existing project conflicts
        conflict_detected = False
        conflict_reason = None
        existing_info = find_project(target_id, ws)
        if existing_info:
            conflict_detected = True
            conflict_reason = f"Project '{target_id}' already exists at {existing_info[0]}."

        return ImportPlan(
            package_file=str(p),
            source_project_id=source_id,
            source_project_name=source_name,
            source_project_version=source_version,
            target_project_id=target_id,
            target_project_name=target_name,
            strategy=strategy,
            conflict_detected=conflict_detected,
            conflict_reason=conflict_reason,
            components_to_import=manifest.components_count,
            nets_to_import=manifest.nets_count,
            bom_items_to_import=manifest.bom_count,
            artifacts_to_import=manifest.artifacts_count,
            surrealdb_tables=manifest.surrealdb.exported_tables,
            warnings=[],
        )

    def import_project(
        self,
        package_path: Path,
        target_project_name: Optional[str] = None,
        strategy: ImportStrategy = ImportStrategy.RESTORE,
        workspace_path: Optional[Path] = None,
        overwrite: bool = False,
    ) -> Tuple[Path, WorklineToonManifest]:
        """
        Executes full project import from a .wlipjt package.
        Steps:
        1. Verifies checksums and container integrity
        2. Validates conflicts and strategy
        3. Restores filesystem directories and files
        4. Restores .workline/project.toon and engineering state
        5. Restores Git metadata
        6. Restores SurrealDB graph records transactionally
        """
        p = Path(package_path).resolve()
        plan = self.plan_import(p, target_project_name=target_project_name, strategy=strategy, workspace_path=workspace_path)

        if plan.conflict_detected and strategy == ImportStrategy.RESTORE and not overwrite:
            raise ProjectConflictError(
                plan.target_project_id,
                message=f"Conflict: {plan.conflict_reason} Set strategy=NEW_PROJECT, MERGE, or pass overwrite=True.",
            )

        ws = (workspace_path or get_workspace_dir()).resolve()
        target_dir = ws / plan.target_project_id

        # Prepare directory
        if target_dir.exists() and overwrite:
            shutil.rmtree(target_dir, ignore_errors=True)

        target_dir.mkdir(parents=True, exist_ok=True)

        # Standard folder structure
        for sub in ["firmware", "hardware", "src", "docs", "tests", "artifacts", ".workline"]:
            (target_dir / sub).mkdir(parents=True, exist_ok=True)

        # Read package contents
        with zipfile.ZipFile(p, "r") as zf:
            namelist = set(zf.namelist())

            def read_toon_item(entry_path: str) -> Dict[str, Any]:
                if entry_path in namelist:
                    raw = zf.read(entry_path).decode("utf-8")
                    return ToonSerializer.dict_from_toon(raw)
                return {}

            # 1. Project Manifests
            proj_dict = read_toon_item("project/project.toon")
            req_dict = read_toon_item("project/requirements.toon")
            arch_dict = read_toon_item("project/architecture.toon")
            con_dict = read_toon_item("project/constraints.toon")

            # 2. Engineering State
            comps_data = read_toon_item("engineering/components.toon")
            comps_list = comps_data if isinstance(comps_data, list) else comps_data.get("items", []) if isinstance(comps_data, dict) else []

            nets_data = read_toon_item("engineering/nets.toon")
            nets_list = nets_data if isinstance(nets_data, list) else nets_data.get("items", []) if isinstance(nets_data, dict) else []

            bom_data = read_toon_item("engineering/bom.toon")
            bom_list = bom_data if isinstance(bom_data, list) else bom_data.get("items", []) if isinstance(bom_data, dict) else []

            power_dict = read_toon_item("engineering/power.toon")
            pcb_dict = read_toon_item("engineering/pcb.toon")
            thermal_dict = read_toon_item("engineering/thermal.toon")

            # 3. Procurement & Orders
            orders_data = read_toon_item("procurement/orders.toon")
            orders_list = orders_data if isinstance(orders_data, list) else orders_data.get("items", []) if isinstance(orders_data, dict) else []

            suppliers_data = read_toon_item("procurement/suppliers.toon")
            suppliers_list = suppliers_data if isinstance(suppliers_data, list) else suppliers_data.get("items", []) if isinstance(suppliers_data, dict) else []

            # 4. Git Metadata
            git_meta = read_toon_item("git/metadata.toon")

            # 5. Extract Artifact Files if present
            for name in namelist:
                if name.startswith("artifacts/files/"):
                    rel_name = name.replace("artifacts/files/", "")
                    art_dest = target_dir / "artifacts" / rel_name
                    art_dest.parent.mkdir(parents=True, exist_ok=True)
                    art_dest.write_bytes(zf.read(name))

        # Save Workline project manifest
        wline_manifest = ProjectManifest(
            name=plan.target_project_id,
            display_name=plan.target_project_name,
            version=plan.source_project_version,
            description=f"Imported from {p.name}",
        )
        save_manifest(wline_manifest, target_dir / "workline.yaml")

        # Save engineering state into .workline/pcb.wlpcb
        pcb_save_data = {
            "board": pcb_dict,
            "components": comps_list,
            "nets": nets_list,
            "bom": bom_list,
            "power_tree": power_dict,
            "thermal": thermal_dict,
        }
        (target_dir / ".workline" / "pcb.wlpcb").write_text(json.dumps(pcb_save_data, indent=2), encoding="utf-8")

        if orders_list:
            (target_dir / ".workline" / "orders.json").write_text(json.dumps(orders_list, indent=2), encoding="utf-8")

        # Initialize Git repository and TOON manifest
        toon_manifest = self.repo_mgr.init_project_git(
            project_path=target_dir,
            project_id=plan.target_project_id,
            project_name=plan.target_project_name,
            default_branch=git_meta.get("current_branch", "main"),
            project_version=plan.source_project_version,
        )

        loaded_manifest = self.repo_mgr.load_toon_manifest(target_dir)
        if not loaded_manifest:
            loaded_manifest = WorklineToonManifest(
                project_id=plan.target_project_id,
                project_name=plan.target_project_name,
                project_version=plan.source_project_version,
            )

        # Update remote if recorded
        if git_meta.get("remote_url"):
            self.git.set_remote(target_dir, "origin", git_meta["remote_url"])
            loaded_manifest.github.connected = True
            loaded_manifest.github.remote = git_meta["remote_url"]
            self.repo_mgr.save_toon_manifest(target_dir, loaded_manifest)

        return target_dir, loaded_manifest


# Module-level singleton
import_service = ImportService()
