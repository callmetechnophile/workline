"""Workspace and project file management operations for Workline."""

import shutil
from pathlib import Path
from typing import List, Optional, Tuple
import yaml

from cli.wline.core.manifest import ProjectManifest, load_manifest, normalize_project_name, save_manifest
from cli.wline.core.paths import (
    clear_active_project,
    ensure_config_dir,
    get_active_project_name,
    get_config_file,
    get_workspace_dir,
)

# Standard Workline 20 engineering project subdirectories
PROJECT_SUBDIRECTORIES: List[str] = [
    "requirements",
    "problem",
    "architecture",
    "subsystems",
    "hardware",
    "datasheets",
    "power",
    "interfaces",
    "schematic",
    "bom",
    "pcb",
    "firmware",
    "tests",
    "validation",
    "telemetry",
    "backend",
    "data",
    "ml",
    "documentation",
    "release",
]


def init_workspace(workspace_path: Optional[Path] = None) -> Tuple[Path, bool]:
    """
    Initialize the Workline local workspace directory.
    Returns:
        (path, already_initialized: bool)
    """
    ws = (workspace_path or get_workspace_dir()).resolve()
    already_initialized = ws.exists() and ws.is_dir()
    ws.mkdir(parents=True, exist_ok=True)
    return ws, already_initialized


def create_project(manifest: ProjectManifest, workspace_path: Optional[Path] = None) -> Path:
    """
    Create a new Workline project in the workspace with all required subdirectories
    and a validated workline.yaml manifest.
    """
    ws = (workspace_path or get_workspace_dir()).resolve()
    ws.mkdir(parents=True, exist_ok=True)

    project_dir = ws / manifest.name
    if project_dir.exists():
        raise FileExistsError(f"Project directory already exists: {project_dir}")

    # Create project root and lifecycle subdirectories
    project_dir.mkdir(parents=True, exist_ok=False)
    for sub in PROJECT_SUBDIRECTORIES:
        (project_dir / sub).mkdir(parents=True, exist_ok=True)

    # Save manifest
    manifest_path = project_dir / "workline.yaml"
    save_manifest(manifest, manifest_path)

    return project_dir


def list_projects(workspace_path: Optional[Path] = None) -> List[ProjectManifest]:
    """
    Discover all valid Workline projects in the workspace.
    Only directories containing a valid workline.yaml are returned.
    """
    ws = (workspace_path or get_workspace_dir()).resolve()
    if not ws.exists() or not ws.is_dir():
        return []

    projects: List[ProjectManifest] = []
    for item in sorted(ws.iterdir()):
        if item.is_dir():
            manifest_file = item / "workline.yaml"
            if manifest_file.exists() and manifest_file.is_file():
                try:
                    manifest = load_manifest(manifest_file)
                    projects.append(manifest)
                except Exception:
                    # Ignore invalid or corrupted directories gracefully
                    continue

    return projects


def find_project(project_name: str, workspace_path: Optional[Path] = None) -> Optional[Tuple[Path, ProjectManifest]]:
    """Find a project by name or normalized name in the workspace."""
    ws = (workspace_path or get_workspace_dir()).resolve()
    normalized = normalize_project_name(project_name)

    target_dir = ws / normalized
    manifest_file = target_dir / "workline.yaml"
    if manifest_file.exists():
        try:
            manifest = load_manifest(manifest_file)
            return target_dir, manifest
        except Exception:
            return None

    # Search through all project manifests as fallback (match by display_name or name)
    for manifest in list_projects(ws):
        if manifest.name == normalized or manifest.display_name.lower() == project_name.strip().lower():
            return ws / manifest.name, manifest

    return None


def delete_project_dir(project_name: str, workspace_path: Optional[Path] = None) -> bool:
    """
    Safely delete a project directory from the workspace.
    Guards against accidental deletion of the root workspace.
    """
    ws = (workspace_path or get_workspace_dir()).resolve()
    project_info = find_project(project_name, ws)
    if not project_info:
        return False

    project_dir, manifest = project_info
    # Safety checks
    if project_dir == ws or project_dir.parent != ws:
        raise ValueError(f"Refusing to delete unsafe directory path: {project_dir}")

    shutil.rmtree(project_dir)

    # Clear active project reference if the deleted project was active
    active = get_active_project_name()
    if active and (active == manifest.name or active == project_name):
        clear_active_project()

    return True


def get_workspace_config() -> dict:
    """Read the configuration from ~/.workline/config.yaml."""
    cfg_file = get_config_file()
    if cfg_file.exists():
        with open(cfg_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data
    return {"workspace": str(get_workspace_dir())}


def update_workspace_config(new_workspace_path: Path) -> dict:
    """Update workspace location in ~/.workline/config.yaml."""
    resolved = new_workspace_path.expanduser().resolve()
    ensure_config_dir()
    cfg_file = get_config_file()

    current_config = get_workspace_config()
    current_config["workspace"] = str(resolved)

    with open(cfg_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(current_config, f, sort_keys=False, default_flow_style=False)

    return current_config
