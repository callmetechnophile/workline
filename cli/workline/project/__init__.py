"""
Project package for WORKLINE CLI.
"""

from cli.workline.project.filesystem import (
    STANDARD_MODULES,
    WL_METADATA_DIR,
    MANIFEST_FILENAME,
    README_FILENAME,
    find_project_root,
    calculate_file_hash,
    discover_project_files,
)
from cli.workline.project.readme import (
    ProjectIdentity,
    parse_readme_wl,
    generate_readme_wl,
)
from cli.workline.project.manifest import (
    ProjectManifestData,
    parse_manifest_wl,
    save_manifest_wl,
    build_manifest_from_filesystem,
)
from cli.workline.project.manager import ProjectManager
from cli.workline.project.validator import (
    ValidationCheck,
    ProjectValidationResult,
    validate_project,
)

__all__ = [
    "STANDARD_MODULES",
    "WL_METADATA_DIR",
    "MANIFEST_FILENAME",
    "README_FILENAME",
    "find_project_root",
    "calculate_file_hash",
    "discover_project_files",
    "ProjectIdentity",
    "parse_readme_wl",
    "generate_readme_wl",
    "ProjectManifestData",
    "parse_manifest_wl",
    "save_manifest_wl",
    "build_manifest_from_filesystem",
    "ProjectManager",
    "ValidationCheck",
    "ProjectValidationResult",
    "validate_project",
]
