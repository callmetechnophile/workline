"""
Parser, validator, and builder for .wl/manifest.wl.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from cli.workline.project.filesystem import (
    STANDARD_MODULES,
    WL_METADATA_DIR,
    MANIFEST_FILENAME,
    calculate_file_hash,
    discover_project_files,
)


@dataclass
class ManifestResourceItem:
    path: str
    count: int = 0
    checksum: Optional[str] = None


@dataclass
class ProjectManifestData:
    schema_version: str = "1.0"
    export_version: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_workline_version: str = "1.0.0"
    project_id: str = "PROJ-DEFAULT"
    project_name: str = "Untitled Project"
    version: str = "1.0"
    domain: str = "Hardware Systems & Engineering"
    status: str = "ACTIVE"
    resources: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    total_files: int = 0
    total_bytes: int = 0
    file_hashes: Dict[str, str] = field(default_factory=dict)


def parse_manifest_wl(manifest_path: Path) -> ProjectManifestData:
    """Parse .wl/manifest.wl into ProjectManifestData."""
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found at {manifest_path}")
        
    content = manifest_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    clean_lines = []
    skip_header = True
    
    for line in lines:
        stripped = line.strip()
        if skip_header:
            if stripped.startswith("WORKLINE_PROJECT_MANIFEST") or (stripped and set(stripped) == {"="}):
                continue
            if ":" in stripped:
                skip_header = False
                clean_lines.append(line)
        else:
            clean_lines.append(line)
            
    parsed = yaml.safe_load("\n".join(clean_lines)) or {}
    
    proj = parsed.get("project", {})
    return ProjectManifestData(
        schema_version=str(parsed.get("schema_version", "1.0")),
        export_version=str(parsed.get("export_version", "")),
        generated_at=str(parsed.get("generated_at", "")),
        source_workline_version=str(parsed.get("source_workline_version", "1.0.0")),
        project_id=str(proj.get("id", "PROJ-DEFAULT")),
        project_name=str(proj.get("name", "Untitled Project")),
        version=str(proj.get("version", "1.0")),
        domain=str(proj.get("domain", "Hardware Systems & Engineering")),
        status=str(proj.get("status", "ACTIVE")),
        resources=parsed.get("resources", {}),
        total_files=int(parsed.get("total_files", 0)),
        total_bytes=int(parsed.get("total_bytes", 0)),
        file_hashes=parsed.get("file_hashes", {}),
    )


def build_manifest_from_filesystem(
    project_root: Path,
    project_id: str,
    project_name: str,
    version: str = "1.0",
    domain: str = "Hardware Systems & Engineering",
    status: str = "ACTIVE",
) -> ProjectManifestData:
    """Scan the project filesystem and build an up-to-date ProjectManifestData."""
    discovered = discover_project_files(project_root)
    
    resources_map: Dict[str, Dict[str, Any]] = {}
    file_hashes: Dict[str, str] = {}
    total_bytes = 0
    
    for mod in STANDARD_MODULES:
        resources_map[mod] = {"path": f"{mod}/", "count": 0}
        
    for rel_posix, abs_path in discovered.items():
        size = abs_path.stat().st_size
        total_bytes += size
        fhash = calculate_file_hash(abs_path)
        file_hashes[rel_posix] = fhash
        
        # Determine module
        parts = rel_posix.split("/")
        if parts:
            top_mod = parts[0]
            if top_mod in resources_map:
                resources_map[top_mod]["count"] += 1
            elif top_mod not in (".wl", "README.wl", ".gitignore", ".worklineignore", ".wlignore"):
                if top_mod not in resources_map:
                    resources_map[top_mod] = {"path": f"{top_mod}/", "count": 1}
                else:
                    resources_map[top_mod]["count"] += 1

    return ProjectManifestData(
        schema_version="1.0",
        export_version=datetime.now(timezone.utc).isoformat(),
        generated_at=datetime.now(timezone.utc).isoformat(),
        source_workline_version="1.0.0",
        project_id=project_id,
        project_name=project_name,
        version=version,
        domain=domain,
        status=status,
        resources=resources_map,
        total_files=len(discovered),
        total_bytes=total_bytes,
        file_hashes=file_hashes,
    )


def save_manifest_wl(manifest: ProjectManifestData, target_path: Path) -> None:
    """Serialize and write ProjectManifestData to .wl/manifest.wl."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "schema_version": manifest.schema_version,
        "export_version": manifest.export_version,
        "generated_at": manifest.generated_at,
        "source_workline_version": manifest.source_workline_version,
        "project": {
            "id": manifest.project_id,
            "name": manifest.project_name,
            "version": manifest.version,
            "domain": manifest.domain,
            "status": manifest.status,
        },
        "resources": manifest.resources,
        "total_files": manifest.total_files,
        "total_bytes": manifest.total_bytes,
        "file_hashes": manifest.file_hashes,
    }
    
    yaml_str = yaml.dump(data, sort_keys=False, default_flow_style=False)
    content = f"WORKLINE_PROJECT_MANIFEST\n==========================\n{yaml_str}"
    target_path.write_text(content, encoding="utf-8")
