"""FastAPI REST endpoints for Workline Project Package (.wlipjt) operations."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from backend.workline.project.backup import backup_service
from backend.workline.project.errors import PackageError
from backend.workline.project.export_service import export_service
from backend.workline.project.import_service import import_service
from backend.workline.project.inspector import PackageInspector
from backend.workline.project.models import (
    ExportOptions,
    ImportPlan,
    ImportStrategy,
    PackageDiff,
    PackageInspection,
    PackageManifest,
)
from cli.wline.core.paths import get_workspace_dir
from cli.wline.core.workspace import find_project

router = APIRouter(prefix="/api/project", tags=["Workline Project Package (.wlipjt)"])


class ExportRequest(BaseModel):
    project_id: str
    include_artifacts: bool = False
    include_vectors: bool = False
    include_git_history: bool = False
    force: bool = False
    output_filename: Optional[str] = None


class ImportRequest(BaseModel):
    package_file: str
    target_name: Optional[str] = None
    strategy: ImportStrategy = ImportStrategy.RESTORE
    overwrite: bool = False


class VerifyRequest(BaseModel):
    package_file: str


class DiffRequest(BaseModel):
    package_file_a: str
    package_file_b: str


class BackupRequest(BaseModel):
    project_id: str
    include_artifacts: bool = False


def _resolve_project_path(project_id: str) -> Path:
    found = find_project(project_id)
    if found:
        return found[0]
    ws_p = get_workspace_dir() / project_id
    if ws_p.exists():
        return ws_p
    raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")


@router.post("/export", response_model=PackageManifest)
def export_project_endpoint(req: ExportRequest):
    """Exports project to portable .wlipjt package."""
    proj_dir = _resolve_project_path(req.project_id)
    opts = ExportOptions(
        include_artifacts=req.include_artifacts,
        include_vectors=req.include_vectors,
        include_git_history=req.include_git_history,
        force=req.force,
    )
    
    out_file = None
    if req.output_filename:
        out_file = Path(req.output_filename)
        if not out_file.is_absolute():
            out_file = get_workspace_dir() / out_file

    try:
        pkg_file, manifest, warnings = export_service.export_project(proj_dir, output_file=out_file, options=opts)
        return manifest
    except PackageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/import")
def import_project_endpoint(req: ImportRequest):
    """Imports project from .wlipjt package."""
    pkg_path = Path(req.package_file)
    if not pkg_path.is_absolute():
        pkg_path = get_workspace_dir() / pkg_path

    if not pkg_path.exists():
        raise HTTPException(status_code=404, detail=f"Package file '{req.package_file}' not found.")

    try:
        target_dir, manifest = import_service.import_project(
            package_path=pkg_path,
            target_project_name=req.target_name,
            strategy=req.strategy,
            overwrite=req.overwrite,
        )
        return {
            "success": True,
            "project_id": manifest.project_id,
            "project_name": manifest.project_name,
            "project_version": manifest.project_version,
            "path": str(target_dir),
        }
    except PackageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify")
def verify_package_endpoint(req: VerifyRequest):
    """Verifies internal SHA-256 checksums of a .wlipjt package."""
    pkg_path = Path(req.package_file)
    if not pkg_path.is_absolute():
        pkg_path = get_workspace_dir() / pkg_path

    if not pkg_path.exists():
        raise HTTPException(status_code=404, detail=f"Package file '{req.package_file}' not found.")

    is_valid, errors = PackageInspector.verify(pkg_path)
    return {
        "valid": is_valid,
        "package_file": str(pkg_path),
        "errors": errors,
    }


@router.get("/package/info", response_model=PackageInspection)
def inspect_package_endpoint(package_file: str = Query(..., description="Path to .wlipjt package")):
    """Performs read-only inspection of a .wlipjt package."""
    pkg_path = Path(package_file)
    if not pkg_path.is_absolute():
        pkg_path = get_workspace_dir() / pkg_path

    if not pkg_path.exists():
        raise HTTPException(status_code=404, detail=f"Package file '{package_file}' not found.")

    try:
        return PackageInspector.inspect(pkg_path)
    except PackageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/diff", response_model=PackageDiff)
def diff_packages_endpoint(req: DiffRequest):
    """Calculates structured diff between two .wlipjt packages."""
    pa = Path(req.package_file_a)
    if not pa.is_absolute():
        pa = get_workspace_dir() / pa

    pb = Path(req.package_file_b)
    if not pb.is_absolute():
        pb = get_workspace_dir() / pb

    if not pa.exists():
        raise HTTPException(status_code=404, detail=f"Package A '{req.package_file_a}' not found.")
    if not pb.exists():
        raise HTTPException(status_code=404, detail=f"Package B '{req.package_file_b}' not found.")

    try:
        return PackageInspector.diff(pa, pb)
    except PackageError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/backup")
def backup_project_endpoint(req: BackupRequest):
    """Creates timestamped .wlipjt backup archive."""
    proj_dir = _resolve_project_path(req.project_id)
    opts = ExportOptions(include_artifacts=req.include_artifacts)
    try:
        pkg_file, manifest, warnings = backup_service.create_backup(proj_dir, options=opts)
        return {
            "success": True,
            "backup_file": str(pkg_file),
            "manifest": manifest,
            "warnings": warnings,
        }
    except PackageError as e:
        raise HTTPException(status_code=400, detail=str(e))
