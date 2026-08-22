"""Domain exceptions for Workline Project Package (.wlipjt) operations."""

from typing import Any, Dict, List, Optional


class PackageError(Exception):
    """Base exception for all .wlipjt package operations."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class CorruptedPackageError(PackageError):
    """Raised when package container is invalid or unreadable."""
    pass


class ChecksumMismatchError(PackageError):
    """Raised when a package file's SHA-256 does not match checksums.toon."""
    def __init__(self, file_path: str, expected_sha: str, actual_sha: str):
        msg = f"Integrity check failed: Checksum mismatch for '{file_path}' (expected {expected_sha[:8]}..., got {actual_sha[:8]}...)."
        super().__init__(msg, {"file_path": file_path, "expected": expected_sha, "actual": actual_sha})
        self.file_path = file_path
        self.expected_sha = expected_sha
        self.actual_sha = actual_sha


class UnsupportedFormatVersionError(PackageError):
    """Raised when format_version in package is not supported by current Workline release."""
    def __init__(self, format_version: int, max_supported: int = 1):
        msg = f"Unsupported package format version: {format_version} (maximum supported version: {max_supported})."
        super().__init__(msg, {"format_version": format_version, "max_supported": max_supported})
        self.format_version = format_version
        self.max_supported = max_supported


class ProjectConflictError(PackageError):
    """Raised when importing a package conflicts with an existing project without overwrite confirmation."""
    def __init__(self, project_id: str, message: Optional[str] = None):
        msg = message or f"Project '{project_id}' already exists in workspace. Choose an import strategy (NEW_PROJECT, RESTORE, or MERGE)."
        super().__init__(msg, {"project_id": project_id})
        self.project_id = project_id


class PackageValidationError(PackageError):
    """Raised when package state validation fails prior to export or after import."""
    def __init__(self, message: str, violations: Optional[List[str]] = None):
        super().__init__(message, {"violations": violations or []})
        self.violations = violations or []


class ExportError(PackageError):
    """Raised when exporting project to .wlipjt fails."""
    pass


class ImportError(PackageError):
    """Raised when importing .wlipjt into workspace fails."""
    pass
