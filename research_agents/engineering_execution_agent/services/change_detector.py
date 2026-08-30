"""
Filesystem change detector and snapshot comparator for EngineeringExecutionAgent (Sections 27, 77).
Detects rogue or out-of-scope modifications before/after task execution.
"""

from fnmatch import fnmatch
import hashlib
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ChangeDetector:
    """Snapshots repository state to verify and audit filesystem modifications."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    def snapshot_state(self, paths_to_watch: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Creates a map of relative file paths to SHA256 checksums.
        """
        state: Dict[str, str] = {}
        if not self.project_root_dir.exists():
            return state

        for root, dirs, files in os.walk(self.project_root_dir):
            # Skip hidden, git, cache, and audit receipt folders
            dirs[:] = [
                d for d in dirs
                if not d.startswith(".")
                and d not in ("__pycache__", "node_modules", "venv", ".venv", "receipts", ".pytest_cache")
            ]
            for f in files:
                full_p = Path(root) / f
                try:
                    rel_p = str(full_p.relative_to(self.project_root_dir)).replace("\\", "/")
                    if "armoriq/receipts" in rel_p or ".pytest_cache" in rel_p:
                        continue
                    file_bytes = full_p.read_bytes()
                    state[rel_p] = hashlib.sha256(file_bytes).hexdigest()
                except Exception:
                    pass

        return state

    def detect_changes(
        self,
        before_state: Dict[str, str],
        after_state: Dict[str, str],
        allowed_paths: Optional[List[str]] = None,
    ) -> Tuple[List[str], List[str]]:
        """
        Compares before and after snapshots.
        Returns:
            (changed_files, out_of_scope_files)
        """
        changed: List[str] = []
        out_of_scope: List[str] = []
        allowed = allowed_paths or []

        all_keys: Set[str] = set(before_state.keys()).union(set(after_state.keys()))

        for k in all_keys:
            # File created or modified or deleted
            if before_state.get(k) != after_state.get(k):
                changed.append(k)

                # Check if this changed file was authorized
                if allowed and "*" not in allowed and "**" not in allowed:
                    is_allowed = False
                    for pat in allowed:
                        clean_pat = pat.replace("\\", "/").strip("./")
                        if fnmatch(k, clean_pat) or (clean_pat.endswith("/**") and k.startswith(clean_pat[:-3])):
                            is_allowed = True
                            break
                    if not is_allowed:
                        out_of_scope.append(k)

        return sorted(changed), sorted(out_of_scope)
