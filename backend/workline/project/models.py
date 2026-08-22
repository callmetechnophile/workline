"""Pydantic data models for Workline Project Package (.wlipjt)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ImportStrategy(str, Enum):
    """Strategy for importing a project package."""
    NEW_PROJECT = "NEW_PROJECT"
    RESTORE = "RESTORE"
    MERGE = "MERGE"


class ArtifactMode(str, Enum):
    """Mode for including artifacts in package."""
    METADATA_ONLY = "METADATA_ONLY"
    INCLUDE_ARTIFACTS = "INCLUDE_ARTIFACTS"


class PackageValidationStatus(str, Enum):
    """Validation status of an exported or inspected package."""
    VALID = "VALID"
    WARNING = "WARNING"
    INVALID = "INVALID"
    FORCED_EXPORT = "FORCED_EXPORT"


class ArtifactMetadata(BaseModel):
    """Metadata describing a project artifact (large file, model, dataset, binary)."""
    artifact_id: str
    name: str
    artifact_type: str = "generic"
    size_bytes: int = 0
    sha256: str
    location: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    included_in_package: bool = False


class GitPackageMetadata(BaseModel):
    """Git versioning metadata included in package."""
    initialized: bool = True
    remote_url: Optional[str] = None
    current_branch: str = "main"
    current_commit: Optional[str] = None
    project_version: str = "0.1.0"
    latest_tag: Optional[str] = None
    included_git_history: bool = False


class SurrealDbPackageMetadata(BaseModel):
    """SurrealDB database metadata included in package."""
    exported_tables: List[str] = Field(default_factory=list)
    total_records: int = 0
    schema_version: int = 1


class QdrantPackageMetadata(BaseModel):
    """Qdrant vector collection metadata (vectors excluded by default)."""
    collections: List[str] = Field(default_factory=list)
    total_documents: int = 0
    embedding_model: str = "text-embedding-3-small"
    document_ids: List[str] = Field(default_factory=list)
    document_hashes: Dict[str, str] = Field(default_factory=dict)
    included_vectors: bool = False

    @field_validator("document_ids", mode="before")
    @classmethod
    def _validate_doc_ids(cls, v: Any) -> List[str]:
        return v if isinstance(v, list) else []

    @field_validator("document_hashes", mode="before")
    @classmethod
    def _validate_doc_hashes(cls, v: Any) -> Dict[str, str]:
        return v if isinstance(v, dict) else {}


class PackageManifest(BaseModel):
    """Root manifest for .wlipjt package (stored in manifest.toon)."""
    format: str = "wlipjt"
    format_version: int = 1
    workline_version: str = "0.1.0"
    schema_version: int = 1
    project_id: str
    project_name: str
    project_version: str = "0.1.0"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    exported_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # High-level entity statistics
    components_count: int = 0
    nets_count: int = 0
    bom_count: int = 0
    pcb_count: int = 0
    artifacts_count: int = 0
    
    git: GitPackageMetadata = Field(default_factory=GitPackageMetadata)
    surrealdb: SurrealDbPackageMetadata = Field(default_factory=SurrealDbPackageMetadata)
    qdrant: QdrantPackageMetadata = Field(default_factory=QdrantPackageMetadata)
    
    validation_status: PackageValidationStatus = PackageValidationStatus.VALID
    checksum: Optional[str] = None
    encrypted: bool = False

    @field_validator("validation_status", mode="before")
    @classmethod
    def _validate_status(cls, v: Any) -> PackageValidationStatus:
        if isinstance(v, PackageValidationStatus):
            return v
        s = str(v).replace("PackageValidationStatus.", "").strip().upper()
        return PackageValidationStatus[s] if s in PackageValidationStatus.__members__ else PackageValidationStatus.VALID


class FileChecksumEntry(BaseModel):
    """Entry in checksums.toon for integrity verification."""
    path: str
    sha256: str
    size_bytes: int = 0


class ChecksumManifest(BaseModel):
    """Checksums of all contained package files."""
    entries: List[FileChecksumEntry] = Field(default_factory=list)


class PackageSizeBreakdown(BaseModel):
    """Size breakdown of package contents."""
    total_package_size_bytes: int = 0
    artifacts_size_bytes: int = 0
    project_state_size_bytes: int = 0
    documentation_size_bytes: int = 0
    git_size_bytes: int = 0


class PackageInspection(BaseModel):
    """Read-only inspection result for a .wlipjt package."""
    valid: bool
    manifest: PackageManifest
    integrity_status: str  # "VALID" or "CORRUPTED"
    size_breakdown: PackageSizeBreakdown
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)


class ImportPlan(BaseModel):
    """Execution plan for importing a project package."""
    package_file: str
    source_project_id: str
    source_project_name: str
    source_project_version: str
    
    target_project_id: str
    target_project_name: str
    strategy: ImportStrategy
    
    conflict_detected: bool = False
    conflict_reason: Optional[str] = None
    
    components_to_import: int = 0
    nets_to_import: int = 0
    bom_items_to_import: int = 0
    artifacts_to_import: int = 0
    
    surrealdb_tables: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PackageDiff(BaseModel):
    """Differences between two .wlipjt packages."""
    source_package: str
    target_package: str
    
    version_diff: str  # e.g. "0.3.0 -> 0.4.0"
    schema_diff: str
    
    components_added: int = 0
    components_removed: int = 0
    components_modified: int = 0
    
    nets_added: int = 0
    nets_removed: int = 0
    
    bom_changed: bool = False
    pcb_changed: bool = False
    constraints_changed: bool = False
    
    details: Dict[str, Any] = Field(default_factory=dict)


class ExportOptions(BaseModel):
    """Configuration options for package export."""
    include_artifacts: bool = False
    include_vectors: bool = False
    include_git_history: bool = False
    force: bool = False
    encrypt: bool = False
    passphrase: Optional[str] = None
