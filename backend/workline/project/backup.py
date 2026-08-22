"""Backup service for creating timestamped .wlipjt archives."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from backend.workline.project.export_service import ExportService, export_service
from backend.workline.project.models import ExportOptions, PackageManifest
from cli.wline.core.paths import get_workspace_dir


class BackupService:
    """
    Manages automated and manual project backups as timestamped .wlipjt packages.
    """

    def __init__(self, exporter: ExportService = export_service):
        self.exporter = exporter

    def create_backup(
        self,
        project_path: Path,
        backup_dir: Optional[Path] = None,
        options: Optional[ExportOptions] = None,
    ) -> Tuple[Path, PackageManifest, List[str]]:
        """
        Creates a timestamped project package archive in the specified backup directory
        (defaults to <workspace>/project-backups/).
        """
        p = Path(project_path).resolve()
        ws = get_workspace_dir().resolve()
        dest_dir = Path(backup_dir).resolve() if backup_dir else (ws / "project-backups")
        dest_dir.mkdir(parents=True, exist_ok=True)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        backup_filename = f"{p.name}-{now_str}.wlipjt"
        target_file = dest_dir / backup_filename

        return self.exporter.export_project(
            project_path=p,
            output_file=target_file,
            options=options,
        )


# Module-level singleton
backup_service = BackupService()
