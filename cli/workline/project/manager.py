"""
ProjectManager for WORKLINE .wl projects.
Handles project creation, discovery, inspection, and status reporting.
"""

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

from cli.workline.project.filesystem import (
    STANDARD_MODULES,
    WL_METADATA_DIR,
    MANIFEST_FILENAME,
    README_FILENAME,
    MOSS_METADATA_FILENAME,
    PROJECT_METADATA_FILENAME,
    find_project_root,
)
from cli.workline.project.readme import (
    ProjectIdentity,
    parse_readme_wl,
    generate_readme_wl,
)
from cli.workline.project.manifest import (
    ProjectManifestData,
    build_manifest_from_filesystem,
    parse_manifest_wl,
    save_manifest_wl,
)
from cli.workline.project.validator import (
    ProjectValidationResult,
    validate_project,
)


def _slugify(text: str) -> str:
    """Generate safe identifier from name."""
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip()).strip("-").lower()
    return clean or "project"


class ProjectManager:
    """Unified manager for WORKLINE .wl projects."""

    def __init__(self, current_dir: Optional[Path] = None):
        self.current_dir = (current_dir or Path.cwd()).resolve()

    def discover_active_project(self) -> Optional[Path]:
        """Locate active project root from current directory or parents."""
        return find_project_root(self.current_dir)

    def init_project(
        self,
        name: str,
        target_dir: Optional[Path] = None,
        project_id: Optional[str] = None,
        description: str = "",
        domain: str = "Hardware Systems & Power Engineering",
        version: str = "1.0",
    ) -> Path:
        """
        Initialize a new valid WORKLINE project filesystem.
        Generates standard directory structure, README.wl, .wl/manifest.wl,
        and clean structural templates.
        """
        slug = _slugify(name)
        root = (target_dir or (self.current_dir / slug)).resolve()
        
        if root.exists() and any(root.iterdir()):
            # Check if already a workline project
            if (root / README_FILENAME).exists():
                raise FileExistsError(f"Directory {root} already contains a WORKLINE project.")

        root.mkdir(parents=True, exist_ok=True)
        (root / WL_METADATA_DIR).mkdir(parents=True, exist_ok=True)
        
        # Create standard module directories
        for mod in STANDARD_MODULES:
            (root / mod).mkdir(parents=True, exist_ok=True)

        # Generate unique project ID if not supplied
        pid = project_id or f"PROJ-{slug.upper()[:8]}"
        
        # Initialize .gitignore and .wlignore (Zero-Secrets invariant)
        gitignore_content = (
            "# WORKLINE Project Ignore\n"
            ".env\n"
            ".env.*\n"
            "*.key\n"
            "*.pem\n"
            "*.token\n"
            "*.secret\n"
            "credentials*\n"
            "private/\n"
            "secrets/\n"
            ".venv/\n"
            "__pycache__/\n"
            "# Derived local retrieval cache (reconstructible via wg index --rebuild)\n"
            ".wl/index/\n"
            ".wl/moss/\n"
        )
        (root / ".gitignore").write_text(gitignore_content, encoding="utf-8")
        (root / ".worklineignore").write_text(gitignore_content, encoding="utf-8")
        (root / ".wlignore").write_text(gitignore_content, encoding="utf-8")

        # Initial structural templates (valid structural metadata only, no fake data)
        self._write_structural_templates(root, pid, name)

        # Build initial manifest and README
        manifest = build_manifest_from_filesystem(
            project_root=root,
            project_id=pid,
            project_name=name,
            version=version,
            domain=domain,
            status="ACTIVE",
        )
        save_manifest_wl(manifest, root / WL_METADATA_DIR / MANIFEST_FILENAME)

        identity = ProjectIdentity(
            name=name,
            project_id=pid,
            version=version,
            status="ACTIVE",
            domain=domain,
            description=description or f"WORKLINE engineering project: {name}",
            schema_version="1.0",
        )
        readme_content = generate_readme_wl(
            identity=identity,
            resource_counts={k: v.get("count", 0) for k, v in manifest.resources.items()},
        )
        (root / README_FILENAME).write_text(readme_content, encoding="utf-8")

        # Create .wl/project.wl and .wl/metadata.wl
        project_wl = (
            f"id: {pid}\n"
            f"name: {name}\n"
            f"version: {version}\n"
            f"domain: {domain}\n"
            f"status: ACTIVE\n"
            f"created_at: {datetime.now(timezone.utc).isoformat()}\n"
        )
        (root / WL_METADATA_DIR / PROJECT_METADATA_FILENAME).write_text(project_wl, encoding="utf-8")

        metadata_wl = (
            "schema_version: 1.0\n"
            f"exported_at: {datetime.now(timezone.utc).isoformat()}\n"
            "source: workline_cli\n"
        )
        (root / WL_METADATA_DIR / "metadata.wl").write_text(metadata_wl, encoding="utf-8")

        # Initial .wl/moss.wl metadata
        moss_wl = (
            "moss:\n"
            "  enabled: true\n"
            f"  index_name: workline_{pid.lower().replace('-', '_')}\n"
            "  schema_version: 1\n"
            "  status: UNINITIALIZED\n"
            "  document_count: 0\n"
            "  runtime: local\n"
            "  indexed_at: null\n"
            "  last_manifest_hash: null\n"
        )
        (root / WL_METADATA_DIR / MOSS_METADATA_FILENAME).write_text(moss_wl, encoding="utf-8")

        # Initial .wl/livekit.wl metadata (Zero-secrets)
        livekit_wl = (
            "livekit:\n"
            "  enabled: true\n"
            "  agent_name: workline-realtime-agent\n"
            "  room_mode: project\n"
            "  realtime: true\n"
            f"  room_prefix: workline-project-\n"
        )
        (root / WL_METADATA_DIR / "livekit.wl").write_text(livekit_wl, encoding="utf-8")

        return root

    def _write_structural_templates(self, root: Path, pid: str, name: str) -> None:
        """Write clean, valid structural templates for initial directories."""
        # 1. Architecture
        arch_system = (
            f"subsystem: system\n"
            f"project_id: {pid}\n"
            f"name: {name} System Architecture\n"
            f"status: DRAFT\n"
            f"description: Master system block diagram and interface hierarchy.\n"
            f"modules:\n"
            f"  - power\n"
            f"  - compute\n"
            f"  - sensors\n"
            f"  - telemetry\n"
        )
        (root / "architecture" / "system.wl").write_text(arch_system, encoding="utf-8")

        # 2. Requirements
        req_power = (
            f"requirement_id: REQ-PWR-001\n"
            f"title: Power Distribution and Voltage Regulation\n"
            f"category: technical\n"
            f"status: DRAFT\n"
            f"subsystem: power\n"
            f"description: System must regulate power rails to maintain operational voltage stability.\n"
            f"constraints:\n"
            f"  nominal_voltage: 12V\n"
            f"  logic_voltage: 3.3V\n"
        )
        (root / "requirements" / "power.wl").write_text(req_power, encoding="utf-8")

        # 3. BOM template
        bom_content = (
            f"bom_id: BOM-{pid}\n"
            f"project_id: {pid}\n"
            f"currency: USD\n"
            f"items: []\n"
        )
        (root / "bom" / "bom.wl").write_text(bom_content, encoding="utf-8")

        # 4. Tasks
        task_init = (
            f"task_id: TASK-001\n"
            f"title: Initial Architecture Definition\n"
            f"status: open\n"
            f"priority: high\n"
            f"assignee: unassigned\n"
            f"description: Complete initial subsystem architecture specification.\n"
        )
        (root / "tasks" / "task-001.wl").write_text(task_init, encoding="utf-8")

    def open_project(self, project_path: Optional[Path] = None) -> Tuple[Path, ProjectIdentity, ProjectManifestData]:
        """Open and verify an existing WORKLINE project."""
        root = find_project_root(project_path or self.current_dir)
        if not root:
            raise FileNotFoundError(
                f"No WORKLINE project found at '{project_path or self.current_dir}'. "
                "Ensure directory contains README.wl or .wl/manifest.wl."
            )
            
        readme = parse_readme_wl(root / README_FILENAME)
        manifest = parse_manifest_wl(root / WL_METADATA_DIR / MANIFEST_FILENAME)
        return root, readme, manifest

    def inspect_project(self, project_path: Optional[Path] = None) -> Dict[str, Any]:
        """Gather full inspection telemetry of the WORKLINE project."""
        root, readme, manifest = self.open_project(project_path)
        
        # Read Moss index metadata
        moss_file = root / WL_METADATA_DIR / MOSS_METADATA_FILENAME
        moss_info = {
            "status": "UNINITIALIZED",
            "document_count": 0,
            "last_indexed": "Never",
            "runtime": "local",
        }
        if moss_file.exists():
            import yaml
            try:
                m_data = yaml.safe_load(moss_file.read_text(encoding="utf-8")) or {}
                m_cfg = m_data.get("moss", {})
                moss_info["status"] = m_cfg.get("status", "READY" if m_cfg.get("document_count", 0) > 0 else "UNINITIALIZED")
                moss_info["document_count"] = m_cfg.get("document_count", 0)
                moss_info["last_indexed"] = m_cfg.get("indexed_at", "Never")
                moss_info["runtime"] = m_cfg.get("runtime", "local")
            except Exception:
                pass

        # Count resource files in each module
        res_counts = {}
        for mod in STANDARD_MODULES:
            mod_dir = root / mod
            if mod_dir.exists():
                count = len([f for f in mod_dir.rglob("*") if f.is_file()])
                res_counts[mod] = count
            else:
                res_counts[mod] = 0

        # Read LiveKit metadata
        lk_file = root / WL_METADATA_DIR / "livekit.wl"
        lk_info = {
            "enabled": True,
            "agent_name": "workline-realtime-agent",
            "room_mode": "project",
            "status": "CONFIGURED" if lk_file.exists() else "DEFAULT",
        }
        if lk_file.exists():
            import yaml
            try:
                lk_data = yaml.safe_load(lk_file.read_text(encoding="utf-8")) or {}
                live_cfg = lk_data.get("livekit", {})
                lk_info["enabled"] = live_cfg.get("enabled", True)
                lk_info["agent_name"] = live_cfg.get("agent_name", "workline-realtime-agent")
                lk_info["room_mode"] = live_cfg.get("room_mode", "project")
            except Exception:
                pass

        return {
            "root": root,
            "identity": readme,
            "manifest": manifest,
            "resources": res_counts,
            "moss": moss_info,
            "livekit": lk_info,
        }

    def check_project(self, project_path: Optional[Path] = None) -> ProjectValidationResult:
        """Run standard validation checks against the project."""
        root = find_project_root(project_path or self.current_dir)
        if not root:
            return ProjectValidationResult(
                is_valid=False,
                errors=[f"Directory is not a WORKLINE project: {project_path or self.current_dir}"],
            )
        return validate_project(root, verify_checksums=True)
