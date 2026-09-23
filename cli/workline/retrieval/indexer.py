"""
ProjectIndexer for WORKLINE .wl projects.
Coordinates filesystem discovery, file parsing, manifest updates, and Moss indexing.
Supports full indexing, incremental updates via file hashes, and watch mode.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Callable, Dict, List, Optional, Set, Tuple

from cli.workline.project.filesystem import (
    calculate_file_hash,
    discover_project_files,
    is_secret_file,
    WL_METADATA_DIR,
    MANIFEST_FILENAME,
    README_FILENAME,
)
from cli.workline.project.manifest import (
    ProjectManifestData,
    build_manifest_from_filesystem,
    parse_manifest_wl,
    save_manifest_wl,
)
from cli.workline.project.readme import parse_readme_wl
from cli.workline.retrieval.moss_adapter import LocalMossAdapter
from cli.workline.retrieval.parsers import parse_file_into_records
from cli.workline.retrieval.record import EngineeringRecord


@dataclass
class IndexingStats:
    project_id: str
    project_name: str
    total_files_scanned: int
    total_records_indexed: int
    changed_files_count: int = 0
    duration_seconds: float = 0.0
    status: str = "READY"
    resource_breakdown: Dict[str, int] = field(default_factory=dict)


class ProjectIndexer:
    """Coordinates indexing of WORKLINE projects into local Moss retrieval layer."""

    def __init__(self, project_root: Path, adapter: Optional[LocalMossAdapter] = None):
        self.project_root = project_root.resolve()
        self.adapter = adapter or LocalMossAdapter(self.project_root)
        self.manifest_file = self.project_root / WL_METADATA_DIR / MANIFEST_FILENAME
        self.readme_file = self.project_root / README_FILENAME

    def _get_project_info(self) -> Tuple[str, str]:
        """Read project ID and name from README or manifest."""
        if self.readme_file.exists():
            readme = parse_readme_wl(self.readme_file)
            return readme.project_id, readme.name
        if self.manifest_file.exists():
            manifest = parse_manifest_wl(self.manifest_file)
            return manifest.project_id, manifest.project_name
        return "PROJ-DEFAULT", self.project_root.name

    def index_full(self, rebuild: bool = False) -> IndexingStats:
        """
        Execute full indexing across all discovered project resources.
        If rebuild=True, clears existing derived index first.
        """
        start_time = time.time()
        project_id, project_name = self._get_project_info()
        
        if rebuild:
            self.adapter.reset_index()

        # 1. Discover all non-secret project files
        discovered_files = discover_project_files(self.project_root)
        
        # 2. Parse all files into normalized records
        all_records: List[EngineeringRecord] = []
        breakdown: Dict[str, int] = {}
        
        for rel_posix, abs_path in discovered_files.items():
            records = parse_file_into_records(abs_path, rel_posix, project_id)
            for r in records:
                all_records.append(r)
                breakdown[r.resource_type] = breakdown.get(r.resource_type, 0) + 1

        # 3. Update manifest.wl with current file hashes
        manifest = build_manifest_from_filesystem(
            project_root=self.project_root,
            project_id=project_id,
            project_name=project_name,
        )
        save_manifest_wl(manifest, self.manifest_file)
        
        manifest_hash = calculate_file_hash(self.manifest_file)

        # 4. Populate Local Moss Index
        self.adapter.reindex_all(all_records, project_id, manifest_hash)
        
        elapsed = time.time() - start_time
        return IndexingStats(
            project_id=project_id,
            project_name=project_name,
            total_files_scanned=len(discovered_files),
            total_records_indexed=len(all_records),
            changed_files_count=len(discovered_files),
            duration_seconds=round(elapsed, 4),
            status="READY",
            resource_breakdown=breakdown,
        )

    def index_incremental(self) -> Tuple[IndexingStats, List[str]]:
        """
        Incrementally index only files that were added, modified, or deleted
        since the last indexing run.
        """
        start_time = time.time()
        project_id, project_name = self._get_project_info()
        
        # Load previous file hashes from manifest
        prev_hashes: Dict[str, str] = {}
        if self.manifest_file.exists():
            try:
                manifest = parse_manifest_wl(self.manifest_file)
                prev_hashes = manifest.file_hashes or {}
            except Exception:
                pass

        # If previous hashes are empty, fall back to full index
        if not prev_hashes:
            stats = self.index_full(rebuild=False)
            return stats, list(discover_project_files(self.project_root).keys())

        # Discover current files and hashes
        current_files = discover_project_files(self.project_root)
        current_hashes: Dict[str, str] = {}
        
        added_or_modified: List[str] = []
        deleted: List[str] = []
        
        for rel_posix, abs_path in current_files.items():
            chash = calculate_file_hash(abs_path)
            current_hashes[rel_posix] = chash
            if rel_posix not in prev_hashes or prev_hashes[rel_posix] != chash:
                added_or_modified.append(rel_posix)

        for rel_posix in prev_hashes.keys():
            if rel_posix not in current_files:
                deleted.append(rel_posix)

        changed_files = added_or_modified + deleted
        if not changed_files:
            elapsed = time.time() - start_time
            return IndexingStats(
                project_id=project_id,
                project_name=project_name,
                total_files_scanned=len(current_files),
                total_records_indexed=self.adapter.get_document_count(),
                changed_files_count=0,
                duration_seconds=round(elapsed, 4),
                status="READY",
            ), []

        # Process deleted files
        for rel_posix in deleted:
            self.adapter.remove_file(rel_posix, project_id)

        # Process added or modified files
        for rel_posix in added_or_modified:
            abs_path = current_files[rel_posix]
            records = parse_file_into_records(abs_path, rel_posix, project_id)
            self.adapter.update_records_for_file(rel_posix, records, project_id)

        # Update manifest
        manifest = build_manifest_from_filesystem(
            project_root=self.project_root,
            project_id=project_id,
            project_name=project_name,
        )
        save_manifest_wl(manifest, self.manifest_file)
        manifest_hash = calculate_file_hash(self.manifest_file)
        
        self.adapter.save_metadata(
            project_id=project_id,
            document_count=self.adapter.get_document_count(),
            manifest_hash=manifest_hash,
            status="READY",
        )

        elapsed = time.time() - start_time
        return IndexingStats(
            project_id=project_id,
            project_name=project_name,
            total_files_scanned=len(current_files),
            total_records_indexed=self.adapter.get_document_count(),
            changed_files_count=len(changed_files),
            duration_seconds=round(elapsed, 4),
            status="READY",
        ), changed_files

    def watch(
        self,
        poll_interval: float = 1.0,
        max_cycles: Optional[int] = None,
        on_change: Optional[Callable[[List[str]], None]] = None,
    ) -> None:
        """
        Continuously monitor project files for modifications and incrementally
        update local index upon detection.
        """
        cycles = 0
        while max_cycles is None or cycles < max_cycles:
            stats, changed = self.index_incremental()
            if changed and on_change:
                on_change(changed)
            time.sleep(poll_interval)
            cycles += 1
