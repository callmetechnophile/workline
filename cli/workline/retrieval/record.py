"""
EngineeringRecord schema for normalized retrieval documents.
Defines metadata, semantic tags, and provenance for project documents.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


from datetime import date, datetime


def _sanitize_val(v: Any) -> Any:
    """Recursively convert datetime and non-primitive types to strings."""
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, dict):
        return {str(k): _sanitize_val(val) for k, val in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_sanitize_val(x) for x in v]
    return v


@dataclass
class EngineeringRecord:
    """Normalized retrieval document representation."""
    record_id: str
    project_id: str
    resource_type: str
    title: str
    path: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    mtime: float = 0.0
    score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert record to dictionary for indexing/serialization."""
        return {
            "record_id": self.record_id,
            "project_id": self.project_id,
            "resource_type": self.resource_type,
            "title": self.title,
            "path": self.path,
            "content": self.content,
            "metadata": _sanitize_val(self.metadata),
            "checksum": self.checksum,
            "mtime": self.mtime,
            "score": self.score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EngineeringRecord":
        """Reconstruct record from dictionary."""
        return cls(
            record_id=data["record_id"],
            project_id=data["project_id"],
            resource_type=data.get("resource_type", "document"),
            title=data.get("title", ""),
            path=data.get("path", ""),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            checksum=data.get("checksum", ""),
            mtime=float(data.get("mtime", 0.0)),
            score=float(data.get("score", 0.0)),
        )
