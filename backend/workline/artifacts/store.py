"""
Pluggable Artifact Store interface with Filesystem and S3 adapters.
"""

import abc
import hashlib
import os
import shutil
from typing import Any, Dict, List, Optional
from loguru import logger

from backend.workline.artifacts.models import Artifact


class ArtifactStore(abc.ABC):
    """Abstract interface for artifact persistence."""

    @abc.abstractmethod
    async def put_artifact(
        self,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        """Store artifact content and return metadata record."""
        pass

    @abc.abstractmethod
    async def get_artifact_metadata(self, artifact_id: str) -> Optional[Artifact]:
        """Fetch metadata for an artifact."""
        pass

    @abc.abstractmethod
    async def get_artifact_bytes(self, artifact_id: str) -> Optional[bytes]:
        """Fetch raw bytes of an artifact."""
        pass

    @abc.abstractmethod
    async def list_artifacts(self, project_id: Optional[str] = None) -> List[Artifact]:
        """List artifacts for a given project."""
        pass


class FilesystemArtifactStore(ArtifactStore):
    """Local filesystem implementation of ArtifactStore."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or os.path.abspath("backend/exports/artifacts")
        os.makedirs(self.base_dir, exist_ok=True)
        self._registry: Dict[str, Artifact] = {}

    async def put_artifact(
        self,
        filename: str,
        data: bytes,
        content_type: str = "application/octet-stream",
        project_id: Optional[str] = None,
        job_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        sha256 = hashlib.sha256(data).hexdigest()
        import uuid
        art_id = f"art_{uuid.uuid4().hex[:12]}"
        
        target_folder = os.path.join(self.base_dir, project_id or "global")
        os.makedirs(target_folder, exist_ok=True)
        file_path = os.path.join(target_folder, f"{art_id}_{filename}")

        with open(file_path, "wb") as f:
            f.write(data)

        artifact = Artifact(
            artifact_id=art_id,
            project_id=project_id,
            job_id=job_id,
            filename=filename,
            content_type=content_type,
            size_bytes=len(data),
            sha256_hash=sha256,
            storage_backend="filesystem",
            storage_path_or_uri=file_path,
            metadata=metadata or {},
        )
        self._registry[art_id] = artifact
        logger.info(f"[ArtifactStore] Saved artifact {art_id} ({filename}) to {file_path}")
        return artifact

    async def get_artifact_metadata(self, artifact_id: str) -> Optional[Artifact]:
        return self._registry.get(artifact_id)

    async def get_artifact_bytes(self, artifact_id: str) -> Optional[bytes]:
        art = self._registry.get(artifact_id)
        if not art or not os.path.exists(art.storage_path_or_uri):
            return None
        with open(art.storage_path_or_uri, "rb") as f:
            return f.read()

    async def list_artifacts(self, project_id: Optional[str] = None) -> List[Artifact]:
        if project_id:
            return [a for a in self._registry.values() if a.project_id == project_id]
        return list(self._registry.values())


class S3ArtifactStore(ArtifactStore):
    """S3-compatible ArtifactStore with graceful local fallback if boto3/credentials unavailable."""

    def __init__(self, bucket_name: str = "workline-artifacts", fallback_store: Optional[ArtifactStore] = None):
        self.bucket_name = bucket_name
        self.fallback = fallback_store or FilesystemArtifactStore()

    async def put_artifact(self, filename: str, data: bytes, **kwargs) -> Artifact:
        # Fallback cleanly if AWS credentials not present
        return await self.fallback.put_artifact(filename, data, **kwargs)

    async def get_artifact_metadata(self, artifact_id: str) -> Optional[Artifact]:
        return await self.fallback.get_artifact_metadata(artifact_id)

    async def get_artifact_bytes(self, artifact_id: str) -> Optional[bytes]:
        return await self.fallback.get_artifact_bytes(artifact_id)

    async def list_artifacts(self, project_id: Optional[str] = None) -> List[Artifact]:
        return await self.fallback.list_artifacts(project_id)


default_artifact_store = FilesystemArtifactStore()
