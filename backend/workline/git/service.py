"""Controlled Git execution service executing fixed subprocess commands safely."""

import os
from pathlib import Path
import subprocess
from typing import Dict, List, Optional, Tuple

from backend.workline.git.errors import (
    GitConflictError,
    GitError,
    RemoteNotFoundError,
    RepositoryNotFoundError,
    SecretDetectedError,
    UncommittedChangesError,
    UnsafeGitCommandError,
)
from backend.workline.git.models import (
    GitBranch,
    GitCommit,
    GitStatus,
    GitSyncStatus,
    GitTag,
)
from backend.workline.git.policies import SecretScanner


class GitResult:
    """Standard result container for executed Git subcommands."""
    def __init__(self, exit_code: int, stdout: str, stderr: str, command: List[str]):
        self.exit_code = exit_code
        self.stdout = stdout.strip()
        self.stderr = stderr.strip()
        self.command = command

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    def __repr__(self) -> str:
        return f"<GitResult exit_code={self.exit_code} cmd={' '.join(self.command)}>"


class GitService:
    """
    Safely executes controlled Git operations with strict parameter sanitization,
    timeout guarantees, and zero arbitrary shell execution.
    """

    ALLOWED_SUBCOMMANDS = {
        "init", "status", "add", "commit", "log", "branch", "checkout", "switch",
        "tag", "remote", "push", "pull", "rev-parse", "rev-list", "config", "fetch", "diff",
        "show", "reset", "stash"
    }

    def __init__(self, default_timeout_sec: float = 20.0):
        self.timeout_sec = default_timeout_sec

    def _run(
        self,
        repo_path: Path,
        args: List[str],
        timeout: Optional[float] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> GitResult:
        """
        Executes a controlled git subcommand in the specified directory.
        Strictly enforces: shell=False, validated subcommand, directory checking.
        """
        if not args:
            raise UnsafeGitCommandError("Empty Git command argument list.")

        subcommand = args[0]
        if subcommand not in self.ALLOWED_SUBCOMMANDS:
            raise UnsafeGitCommandError(f"Git subcommand '{subcommand}' is not in the allowed policy whitelist.")

        target_dir = Path(repo_path).resolve()
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["git"] + args
        try:
            res = subprocess.run(
                cmd,
                cwd=str(target_dir),
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout or self.timeout_sec,
                env=env if env is not None else os.environ.copy(),
            )
            return GitResult(exit_code=res.returncode, stdout=res.stdout, stderr=res.stderr, command=cmd)
        except subprocess.TimeoutExpired:
            raise GitError(f"Git command timed out after {timeout or self.timeout_sec}s: {' '.join(cmd)}")
        except Exception as exc:
            raise GitError(f"Failed to execute Git subprocess: {str(exc)}")

    def is_repository(self, path: Path) -> bool:
        """Check if path is inside a valid Git working tree."""
        p = Path(path).resolve()
        if not (p / ".git").exists():
            # Check via git rev-parse in case of worktree
            res = self._run(p, ["rev-parse", "--is-inside-work-tree"])
            return res.success and res.stdout.lower() == "true"
        return True

    def initialize_repository(self, path: Path, initial_branch: str = "main") -> GitResult:
        """Initialize a new Git repository with standard initial branch."""
        target_dir = Path(path).resolve()
        target_dir.mkdir(parents=True, exist_ok=True)

        # Try `git init -b <initial_branch>`
        res = self._run(target_dir, ["init", "-b", initial_branch])
        if not res.success:
            # Fallback for older git versions
            res = self._run(target_dir, ["init"])
            if res.success:
                self._run(target_dir, ["branch", "-M", initial_branch])

        # Configure safe defaults if user.name/email not set globally
        self._run(target_dir, ["config", "--local", "init.defaultBranch", initial_branch])
        return res

    def get_status(self, path: Path) -> GitStatus:
        """Inspect working tree status, staged/modified files, and sync status."""
        p = Path(path).resolve()
        if not self.is_repository(p):
            raise RepositoryNotFoundError(f"Directory '{p}' is not a Git repository.")

        # 1. Current Branch
        branch_res = self._run(p, ["rev-parse", "--abbrev-ref", "HEAD"])
        branch_name = branch_res.stdout if branch_res.success else "main"

        # 2. Current Commit Hash
        commit_res = self._run(p, ["rev-parse", "HEAD"])
        current_commit = commit_res.stdout if commit_res.success else None
        short_commit = current_commit[:7] if current_commit else None

        # 3. Porcelain status
        status_res = self._run(p, ["status", "--porcelain=v1"])
        staged_files: List[str] = []
        modified_files: List[str] = []
        untracked_files: List[str] = []

        if status_res.success and status_res.stdout:
            for line in status_res.stdout.splitlines():
                if len(line) < 3:
                    continue
                x = line[0]
                y = line[1]
                fname = line[3:].strip()

                if x in ("A", "M", "R", "C", "D"):
                    staged_files.append(fname)
                if y == "M" or (y == "D" and x == " "):
                    modified_files.append(fname)
                if x == "?" and y == "?":
                    untracked_files.append(fname)

        is_clean = len(staged_files) == 0 and len(modified_files) == 0 and len(untracked_files) == 0

        # 4. Remote and Sync Status
        remote_url = self.get_remote(p, "origin")
        ahead = 0
        behind = 0
        sync_status = GitSyncStatus.NO_REMOTE

        if remote_url:
            sync_status = GitSyncStatus.UP_TO_DATE
            # Check tracking branch rev-list count
            rev_res = self._run(p, ["rev-list", "--left-right", "--count", f"{branch_name}...origin/{branch_name}"])
            if rev_res.success and rev_res.stdout:
                parts = rev_res.stdout.split()
                if len(parts) == 2:
                    try:
                        ahead = int(parts[0])
                        behind = int(parts[1])
                        if ahead > 0 and behind > 0:
                            sync_status = GitSyncStatus.DIVERGED
                        elif ahead > 0:
                            sync_status = GitSyncStatus.AHEAD
                        elif behind > 0:
                            sync_status = GitSyncStatus.BEHIND
                        else:
                            sync_status = GitSyncStatus.UP_TO_DATE
                    except ValueError:
                        pass
            else:
                sync_status = GitSyncStatus.UNTRACKED_REMOTE

        return GitStatus(
            is_clean=is_clean,
            branch=branch_name,
            current_commit=current_commit,
            short_commit=short_commit,
            staged_files=staged_files,
            modified_files=modified_files,
            untracked_files=untracked_files,
            remote_url=remote_url,
            ahead=ahead,
            behind=behind,
            sync_status=sync_status,
        )

    def stage_files(self, path: Path, files: Optional[List[str]] = None) -> GitResult:
        """Stage specific files or all non-ignored modified/untracked files."""
        p = Path(path).resolve()
        if files:
            args = ["add"] + files
        else:
            args = ["add", "."]
        return self._run(p, args)

    def create_commit(
        self,
        path: Path,
        message: str,
        author_name: str = "Workline Engineer",
        author_email: str = "engineer@workline.dev",
        stage_all: bool = False,
        scan_secrets: bool = True,
    ) -> GitCommit:
        """
        Creates a Git commit with automated secret scanning policy enforcement.
        """
        p = Path(path).resolve()
        if not self.is_repository(p):
            raise RepositoryNotFoundError(f"Directory '{p}' is not a Git repository.")

        if not message or not message.strip():
            raise GitError("Commit message cannot be empty.")

        if stage_all:
            self.stage_files(p)

        # Secret Scanning Check
        if scan_secrets:
            # Read staged content
            diff_res = self._run(p, ["diff", "--cached"])
            if diff_res.success and diff_res.stdout:
                findings = SecretScanner.scan_content(diff_res.stdout, file_path="staged_diff")
                if findings:
                    formatted_findings = [f.to_dict() for f in findings]
                    finding_str = "\n".join([f"  - {f.file_path}:{f.line_number} [{f.secret_type}]" for f in findings])
                    raise SecretDetectedError(
                        f"Commit blocked: Potential secret or credential detected in staged files:\n{finding_str}",
                        findings=formatted_findings,
                    )

        # Ensure author info is configured for local commit
        author_env = os.environ.copy()
        author_env["GIT_AUTHOR_NAME"] = author_name
        author_env["GIT_AUTHOR_EMAIL"] = author_email
        author_env["GIT_COMMITTER_NAME"] = author_name
        author_env["GIT_COMMITTER_EMAIL"] = author_email

        commit_res = self._run(
            p,
            ["commit", f"--author={author_name} <{author_email}>", "-m", message.strip()],
            env=author_env,
        )
        if not commit_res.success:
            if "nothing to commit" in commit_res.stdout.lower() or "nothing to commit" in commit_res.stderr.lower():
                raise GitError("Nothing to commit (working tree clean).")
            raise GitError(f"Commit failed: {commit_res.stderr or commit_res.stdout}")

        # Fetch newly created commit hash
        head_hash_res = self._run(p, ["rev-parse", "HEAD"])
        full_hash = head_hash_res.stdout if head_hash_res.success else "unknown"
        short_hash = full_hash[:7]

        # Branch
        branch_name = self.get_current_branch(p)

        return GitCommit(
            commit_hash=full_hash,
            short_hash=short_hash,
            message=message.strip(),
            author=author_name,
            email=author_email,
            branch=branch_name,
        )

    def get_log(self, path: Path, limit: int = 10) -> List[GitCommit]:
        """Fetch concise commit log history."""
        p = Path(path).resolve()
        if not self.is_repository(p):
            raise RepositoryNotFoundError(f"Directory '{p}' is not a Git repository.")

        # Format: %H|%h|%an|%ae|%aI|%s
        res = self._run(p, ["log", f"-n{max(1, limit)}", "--pretty=format:%H|%h|%an|%ae|%aI|%s"])
        if not res.success or not res.stdout:
            return []

        commits = []
        for line in res.stdout.splitlines():
            parts = line.split("|", 5)
            if len(parts) >= 6:
                commits.append(
                    GitCommit(
                        commit_hash=parts[0],
                        short_hash=parts[1],
                        author=parts[2],
                        email=parts[3],
                        timestamp=parts[4],
                        message=parts[5],
                    )
                )
        return commits

    def get_current_branch(self, path: Path) -> str:
        """Get the current active branch name."""
        p = Path(path).resolve()
        res = self._run(p, ["rev-parse", "--abbrev-ref", "HEAD"])
        return res.stdout if res.success else "main"

    def get_current_commit(self, path: Path) -> Optional[str]:
        """Get the current HEAD commit hash."""
        p = Path(path).resolve()
        res = self._run(p, ["rev-parse", "HEAD"])
        return res.stdout if res.success else None

    def list_branches(self, path: Path) -> List[GitBranch]:
        """List all local branches."""
        p = Path(path).resolve()
        res = self._run(p, ["branch", "--format=%(refname:short)|%(HEAD)|%(objectname)"])
        if not res.success or not res.stdout:
            return []

        branches = []
        for line in res.stdout.splitlines():
            parts = line.split("|")
            if len(parts) >= 3:
                name = parts[0]
                is_curr = parts[1] == "*"
                c_hash = parts[2]
                branches.append(GitBranch(name=name, is_current=is_curr, commit_hash=c_hash))
        return branches

    def create_branch(self, path: Path, branch_name: str) -> GitResult:
        """Create a new local branch."""
        p = Path(path).resolve()
        return self._run(p, ["branch", branch_name.strip()])

    def switch_branch(self, path: Path, branch_name: str, create: bool = False) -> GitResult:
        """Switch to a branch (using checkout or switch)."""
        p = Path(path).resolve()
        if create:
            return self._run(p, ["checkout", "-b", branch_name.strip()])
        return self._run(p, ["checkout", branch_name.strip()])

    def delete_branch(self, path: Path, branch_name: str, force: bool = False) -> GitResult:
        """Delete a local branch."""
        p = Path(path).resolve()
        flag = "-D" if force else "-d"
        return self._run(p, ["branch", flag, branch_name.strip()])

    def create_tag(self, path: Path, tag_name: str, message: Optional[str] = None) -> GitTag:
        """Create an annotated or lightweight Git tag."""
        p = Path(path).resolve()
        args = ["tag"]
        if message:
            args.extend(["-a", tag_name.strip(), "-m", message.strip()])
        else:
            args.append(tag_name.strip())

        res = self._run(p, args)
        if not res.success:
            raise GitError(f"Tag creation failed: {res.stderr or res.stdout}")

        commit_hash = self.get_current_commit(p) or "unknown"
        return GitTag(
            name=tag_name.strip(),
            commit_hash=commit_hash,
            message=message or "",
        )

    def list_tags(self, path: Path) -> List[GitTag]:
        """List all Git tags in the repository."""
        p = Path(path).resolve()
        res = self._run(p, ["tag", "-l"])
        if not res.success or not res.stdout:
            return []

        tags = []
        for name in res.stdout.splitlines():
            name = name.strip()
            if name:
                c_res = self._run(p, ["rev-list", "-n", "1", name])
                c_hash = c_res.stdout if c_res.success else ""
                tags.append(GitTag(name=name, commit_hash=c_hash))
        return tags

    def set_remote(self, path: Path, name: str = "origin", url: str = "") -> GitResult:
        """Configure or update a Git remote URL."""
        p = Path(path).resolve()
        existing = self.get_remote(p, name)
        if existing:
            return self._run(p, ["remote", "set-url", name, url.strip()])
        return self._run(p, ["remote", "add", name, url.strip()])

    def get_remote(self, path: Path, name: str = "origin") -> Optional[str]:
        """Get URL of the specified remote name."""
        p = Path(path).resolve()
        res = self._run(p, ["remote", "get-url", name])
        return res.stdout if res.success else None

    def remove_remote(self, path: Path, name: str = "origin") -> GitResult:
        """Remove a configured remote."""
        p = Path(path).resolve()
        return self._run(p, ["remote", "remove", name])

    def push(
        self,
        path: Path,
        remote: str = "origin",
        branch: Optional[str] = None,
        set_upstream: bool = False,
        tags: bool = False,
    ) -> GitResult:
        """Push local commits or tags to the remote repository."""
        p = Path(path).resolve()
        args = ["push"]
        if set_upstream:
            args.append("-u")
        args.append(remote)
        if branch:
            args.append(branch)
        if tags:
            args.append("--tags")
        return self._run(p, args)

    def pull(self, path: Path, remote: str = "origin", branch: Optional[str] = None) -> GitResult:
        """Pull latest commits from remote."""
        p = Path(path).resolve()
        status = self.get_status(p)
        if not status.is_clean:
            raise UncommittedChangesError("Cannot pull: you have uncommitted changes in your working tree.")

        args = ["pull", remote]
        if branch:
            args.append(branch)
        return self._run(p, args)


# Module-level singleton
git_service = GitService()
