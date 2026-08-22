"""Domain exceptions for Workline Git and GitHub version control operations."""


class GitError(Exception):
    """Base exception for all Git operations."""
    pass


class RepositoryNotFoundError(GitError):
    """Raised when the specified directory is not a Git repository."""
    pass


class SecretDetectedError(GitError):
    """Raised when potential credentials or secrets are detected prior to commit."""
    def __init__(self, message: str, findings: list = None):
        super().__init__(message)
        self.findings = findings or []


class UncommittedChangesError(GitError):
    """Raised when an operation is unsafe due to uncommitted working tree changes."""
    pass


class GitHubAuthError(GitError):
    """Raised when GitHub authentication is missing, invalid, or expired."""
    pass


class GitHubRepoExistsError(GitError):
    """Raised when attempting to create a repository that already exists on GitHub."""
    def __init__(self, repo_name: str, owner: str = ""):
        full = f"{owner}/{repo_name}" if owner else repo_name
        super().__init__(f"GitHub repository '{full}' already exists.")
        self.repo_name = repo_name
        self.owner = owner


class InvalidRepoNameError(GitError):
    """Raised when a repository name does not comply with GitHub naming rules."""
    pass


class RemoteNotFoundError(GitError):
    """Raised when the specified Git remote is not configured."""
    pass


class GitConflictError(GitError):
    """Raised when merge or rebase conflicts occur."""
    pass


class UnsafeGitCommandError(GitError):
    """Raised when an unsafe or unapproved Git command is attempted."""
    pass
