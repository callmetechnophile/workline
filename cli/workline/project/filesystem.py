"""
Filesystem layer for WORKLINE .wl projects.
Implements the open standard WORKLINE project directory layout and discovery.
"""

import hashlib
import fnmatch
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

STANDARD_MODULES: List[str] = [
    "requirements",
    "architecture",
    "components",
    "bom",
    "research",
    "documents",
    "analysis",
    "decisions",
    "tasks",
    "team",
    "agents",
    "history",
]

WL_METADATA_DIR = ".wl"
MANIFEST_FILENAME = "manifest.wl"
README_FILENAME = "README.wl"
MOSS_METADATA_FILENAME = "moss.wl"
PROJECT_METADATA_FILENAME = "project.wl"


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Locate the root of a WORKLINE project by searching upwards from start_path.
    A valid project contains README.wl and/or .wl/manifest.wl.
    """
    current = (start_path or Path.cwd()).resolve()
    
    # If the user passed a file, take its parent directory
    if current.is_file():
        current = current.parent
        
    for p in [current, *current.parents]:
        readme = p / README_FILENAME
        manifest = p / WL_METADATA_DIR / MANIFEST_FILENAME
        if readme.exists() or manifest.exists():
            return p
            
    return None


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha.update(chunk)
    return sha.hexdigest()


def is_secret_file(rel_path: str, secret_patterns: Set[str]) -> bool:
    """
    Check if a relative path matches any forbidden secret patterns.
    Enforces the zero-secrets invariant.
    """
    norm = rel_path.replace("\\", "/")
    filename = Path(norm).name
    
    for pattern in secret_patterns:
        # Match against filename or full relative path
        if fnmatch.fnmatch(filename, pattern) or fnmatch.fnmatch(norm, pattern):
            return True
        if pattern.endswith("/*") and (norm.startswith(pattern[:-2]) or f"/{pattern[:-2]}/" in f"/{norm}/"):
            return True
            
    return False


def discover_project_files(
    project_root: Path,
    secret_patterns: Optional[Set[str]] = None,
) -> Dict[str, Path]:
    """
    Discover all candidate project files within project_root, strictly excluding
    secrets, runtime caches, git repositories, and derived indexes.
    Returns a dictionary mapping relative_posix_path -> absolute_path.
    """
    patterns = secret_patterns or {
        ".env", ".env.*", "*.env", "credentials*", "*.pem", "*.key",
        "*.token", "*.secret", "id_rsa*", "id_ed25519*", "private*",
        "secrets/*", ".git/*", "__pycache__/*", "node_modules/*", ".venv/*",
        ".wl/index/*", ".wl/index", ".wl/moss/*", ".wl/manifest.wl", ".wl/moss.wl",
    }
    
    discovered: Dict[str, Path] = {}
    project_root = project_root.resolve()
    
    for item in project_root.rglob("*"):
        if not item.is_file():
            continue
            
        rel_posix = item.relative_to(project_root).as_posix()
        
        # Check against secret & cache patterns
        if is_secret_file(rel_posix, patterns):
            continue
            
        discovered[rel_posix] = item
        
    return discovered
