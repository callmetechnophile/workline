"""
Portable project packaging and export/import for WORKLINE .wl projects.
Packages self-contained .workline.zip archives with zero-secrets guarantee.
"""

from pathlib import Path
from typing import Optional, Set
import zipfile

from cli.workline.project.filesystem import discover_project_files, find_project_root
from cli.workline.project.readme import parse_readme_wl


def export_project_zip(
    project_root: Path,
    output_zip: Optional[Path] = None,
) -> Path:
    """
    Bundle a WORKLINE project into a portable .workline.zip archive.
    Strictly excludes secrets, private keys, local virtualenvs, git files,
    and derived local index binaries (.wl/index/).
    """
    root = (find_project_root(project_root) or project_root).resolve()
    if not (root / "README.wl").exists():
        raise FileNotFoundError(f"Cannot export: {root} is not a valid WORKLINE project (missing README.wl).")
        
    try:
        identity = parse_readme_wl(root / "README.wl")
        project_name = identity.project_id.lower()
    except Exception:
        project_name = root.name.lower()

    dest = output_zip or (root.parent / f"{project_name}.workline.zip")
    dest = dest.resolve()
    
    # Exclude derived index from export
    export_patterns: Set[str] = {
        ".env", ".env.*", "*.env", "credentials*", "*.pem", "*.key",
        "*.token", "*.secret", "id_rsa*", "id_ed25519*", "private*",
        "secrets/*", ".git/*", "__pycache__/*", "node_modules/*", ".venv/*",
        ".wl/index/*", ".wl/moss/*",
    }
    
    files_to_pack = discover_project_files(root, secret_patterns=export_patterns)
    
    with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zip_out:
        for rel_posix, abs_path in files_to_pack.items():
            zip_out.write(abs_path, arcname=rel_posix)

    return dest


def import_project_zip(
    zip_path: Path,
    target_dir: Path,
) -> Path:
    """
    Extract and initialize a WORKLINE project from a .workline.zip archive.
    """
    zip_path = zip_path.resolve()
    if not zip_path.exists():
        raise FileNotFoundError(f"Export zip not found: {zip_path}")
        
    dest = target_dir.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, "r") as zip_in:
        zip_in.extractall(dest)
        
    return dest
