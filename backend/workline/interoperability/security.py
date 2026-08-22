"""Security abstractions, artifact references, and payload sanitization for external agent boundaries."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ArtifactReference(BaseModel):
    """Safe, scoped reference to an engineering artifact without leaking absolute filesystem paths."""
    artifact_id: str
    type: str = Field(..., description="MIME type or artifact kind (e.g. 'application/json', 'pcb/schematic')")
    size: int = Field(default=0, description="Size in bytes")
    sha256: str = Field(..., description="Deterministic integrity hash")
    access_scope: str = Field(default="read-only", description="Permitted access scope")
    expires_at: Optional[str] = None


# Pattern to identify and redact sensitive environment keys, API tokens, passwords, and file paths
SENSITIVE_KEY_PATTERNS = [
    re.compile(r"(?i)api[_-]?key"),
    re.compile(r"(?i)secret"),
    re.compile(r"(?i)password"),
    re.compile(r"(?i)token"),
    re.compile(r"(?i)private[_-]?key"),
    re.compile(r"(?i)authorization"),
    re.compile(r"(?i)credential"),
    re.compile(r"(?i)wallet"),
    re.compile(r"(?i)encryption[_-]?key"),
    re.compile(r"(?i)connection[_-]?string"),
]

# Sensitive path prefixes that must never be exposed to external agents
SENSITIVE_PATH_PATTERNS = [
    re.compile(r"[a-zA-Z]:\\[^ \t\n\r\f\v]+"),  # Windows absolute paths
    re.compile(r"/(?:home|Users|root|etc|var|tmp|opt)/[^ \t\n\r\f\v]+"),  # Unix paths
]


class SecuritySanitizer:
    """Sanitizes context, inputs, and outputs crossing external agent boundaries."""

    @classmethod
    def sanitize_payload(cls, data: Any) -> Any:
        """Recursively sanitize a dictionary, list, or string to remove sensitive tokens and paths."""
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(p.search(k) for p in SENSITIVE_KEY_PATTERNS):
                    sanitized[k] = "[REDACTED_SECRET]"
                else:
                    sanitized[k] = cls.sanitize_payload(v)
            return sanitized
        elif isinstance(data, list):
            return [cls.sanitize_payload(item) for item in data]
        elif isinstance(data, str):
            res = data
            for path_pattern in SENSITIVE_PATH_PATTERNS:
                res = path_pattern.sub("[RESTRICTED_INTERNAL_PATH]", res)
            return res
        return data

    @classmethod
    def validate_team_project_isolation(
        cls,
        request_team_id: str,
        request_project_id: str,
        target_team_id: str,
        target_project_id: str,
    ) -> bool:
        """Strictly verify that the task request belongs to the authorized project and team."""
        if not request_team_id or not request_project_id:
            return False
        return (request_team_id == target_team_id) and (request_project_id == target_project_id)
