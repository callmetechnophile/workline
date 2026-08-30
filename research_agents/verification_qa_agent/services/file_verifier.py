"""
File inspection and change verification service for VerificationQAAgent (Sections 8 & 9).
Compares actual files against expected plan outputs and flags unauthorized or unexpected modifications.
"""

from fnmatch import fnmatch
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from research_agents.verification_qa_agent.schemas import ChangeObject


class FileVerifier:
    """Verifies file tree integrity, expected outputs, and detects unauthorized files."""

    def __init__(self, project_root_dir: Optional[str] = None):
        self.project_root_dir = Path(project_root_dir or os.getcwd()).resolve()

    def verify_changes(
        self,
        actual_changed_files: List[str],
        plan_tasks: List[Dict[str, Any]],
        allowed_paths: List[str],
    ) -> List[ChangeObject]:
        """
        Compares expected vs actual files and verifies scope authorization.
        """
        results: List[ChangeObject] = []
        expected_files: Set[str] = set()
        task_file_map: Dict[str, str] = {}

        # 1. Collect expected outputs from implementation plan
        for t in plan_tasks:
            t_id = t.get("task_id", "TASK")
            target = t.get("target_file")
            if target:
                norm_t = target.replace("\\", "/").strip("./")
                expected_files.add(norm_t)
                task_file_map[norm_t] = t_id

            for exp in t.get("expected_outputs", []):
                norm_exp = exp.replace("\\", "/").strip("./")
                expected_files.add(norm_exp)
                task_file_map[norm_exp] = t_id

        # 2. Check each actual changed file
        for act in actual_changed_files:
            norm_act = act.replace("\\", "/").strip("./")

            # Check if this change was authorized under allowed_paths
            is_authorized = True
            if allowed_paths and "*" not in allowed_paths and "**" not in allowed_paths:
                is_authorized = False
                for pat in allowed_paths:
                    clean_pat = pat.replace("\\", "/").strip("./")
                    if fnmatch(norm_act, clean_pat) or (clean_pat.endswith("/**") and norm_act.startswith(clean_pat[:-3])):
                        is_authorized = True
                        break

            # Check if file was expected
            is_expected = norm_act in expected_files

            # Check physical file existence on disk
            full_path = self.project_root_dir / norm_act
            exists = full_path.exists()

            change_type = "modified"
            if not is_expected and not is_authorized:
                change_type = "unexpected"
            elif exists:
                change_type = "created"
            else:
                change_type = "deleted"

            status = "PASS" if (is_authorized and is_expected and exists) else "FAIL"

            results.append(
                ChangeObject(
                    file=norm_act,
                    expected=is_expected,
                    actual=exists,
                    change_type=change_type,
                    authorized=is_authorized,
                    task_id=task_file_map.get(norm_act),
                    status=status,
                )
            )

        # 3. Check for any expected files that were completely missing
        for exp_f in expected_files:
            if exp_f not in [r.file for r in results]:
                full_path = self.project_root_dir / exp_f
                exists = full_path.exists()
                results.append(
                    ChangeObject(
                        file=exp_f,
                        expected=True,
                        actual=exists,
                        change_type="created" if exists else "deleted",
                        authorized=True,
                        task_id=task_file_map.get(exp_f),
                        status="PASS" if exists else "FAIL",
                    )
                )

        return results
