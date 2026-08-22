"""GitHub remote URL and repository reference normalization."""

import re
from typing import Optional, Tuple


def parse_github_repo_spec(spec: str) -> Tuple[Optional[str], str]:
    """
    Parses a repository specification (owner/repo or URL) into (owner, repo_name).
    Examples:
        'autonomous-rover' -> (None, 'autonomous-rover')
        'acme-corp/autonomous-rover' -> ('acme-corp', 'autonomous-rover')
        'https://github.com/acme-corp/autonomous-rover.git' -> ('acme-corp', 'autonomous-rover')
        'git@github.com:acme-corp/autonomous-rover.git' -> ('acme-corp', 'autonomous-rover')
    """
    cleaned = spec.strip()
    # Remove trailing .git
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    # HTTPS URL: https://github.com/owner/repo
    https_match = re.match(r"^https?://github\.com/([^/]+)/([^/]+)$", cleaned)
    if https_match:
        return https_match.group(1), https_match.group(2)

    # SSH URL: git@github.com:owner/repo
    ssh_match = re.match(r"^git@github\.com:([^/]+)/([^/]+)$", cleaned)
    if ssh_match:
        return ssh_match.group(1), ssh_match.group(2)

    # owner/repo
    if "/" in cleaned:
        parts = cleaned.split("/", 1)
        return parts[0].strip(), parts[1].strip()

    # Just repo name
    return None, cleaned


def normalize_github_url(owner: str, repo_name: str, use_ssh: bool = False) -> str:
    """
    Generates a clean, token-free GitHub clone URL.
    """
    clean_owner = owner.strip()
    clean_repo = repo_name.strip()
    if clean_repo.endswith(".git"):
        clean_repo = clean_repo[:-4]

    if use_ssh:
        return f"git@github.com:{clean_owner}/{clean_repo}.git"
    return f"https://github.com/{clean_owner}/{clean_repo}.git"


def get_html_url(owner: str, repo_name: str) -> str:
    """Generates the web browser URL for a repository."""
    clean_owner = owner.strip()
    clean_repo = repo_name.strip()
    if clean_repo.endswith(".git"):
        clean_repo = clean_repo[:-4]
    return f"https://github.com/{clean_owner}/{clean_repo}"
