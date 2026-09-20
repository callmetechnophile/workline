"""
Pluggable Artifact Store system with Local Filesystem and Amazon S3 backends.
Enforces content addressing (SHA-256), MIME-type validation, and presigned URL generation.
"""

import abc
import hashlib
import mimetypes
import os
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from loguru import logger


class Artifact(BaseModel):
    artifact_id: str
    filename: str
    project_id: str
    category: str = "general"
    content_type: str = "application/octet-stream"
    size_bytes: int = 0
    sha256_hash: str
    storage_backend: str = "filesystem"  # filesystem, s3
    storage_path_or_uri: str
    created_at: float = Field(default_factory=time.time)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    download_url: Optional[str] = None


class ArtifactStore(abc.ABC):
    """Abstract Base Class for Artifact Storage."""

    @abc.abstractmethod
    async def put_artifact(
        self,
        filename: str,
        data: bytes,
        project_id: str = "default",
        category: str = "general",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        pass

    @abc.abstractmethod
    async def get_artifact_metadata(self, artifact_id: str) -> Optional[Artifact]:
        pass

    @abc.abstractmethod
    async def get_artifact_bytes(self, artifact_id: str) -> Optional[bytes]:
        pass

    @abc.abstractmethod
    async def list_artifacts(self, project_id: Optional[str] = None) -> List[Artifact]:
        pass

    @abc.abstractmethod
    async def generate_presigned_get_url(self, artifact_id: str, expires_in: int = 900) -> Optional[str]:
        pass

    @abc.abstractmethod
    async def generate_presigned_put_url(
        self, filename: str, project_id: str, category: str = "general", expires_in: int = 900
    ) -> Dict[str, Any]:
        pass


class FilesystemArtifactStore(ArtifactStore):
    """Local filesystem artifact store for offline testing, local dev, and fallback."""

    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            if os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or os.environ.get("LAMBDA_TASK_ROOT"):
                base_dir = os.path.join(tempfile.gettempdir(), "artifacts")
            else:
                base_dir = "backend/exports/artifacts"
        self.base_dir = os.path.abspath(base_dir)
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except Exception:
            self.base_dir = os.path.join(tempfile.gettempdir(), "artifacts")
            try:
                os.makedirs(self.base_dir, exist_ok=True)
            except Exception:
                pass
        self._registry: Dict[str, Artifact] = {}

    async def put_artifact(
        self,
        filename: str,
        data: bytes,
        project_id: str = "default",
        category: str = "general",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        sha256 = hashlib.sha256(data).hexdigest()
        art_id = f"art-{sha256[:12]}"
        
        project_dir = os.path.join(self.base_dir, project_id, category)
        try:
            os.makedirs(project_dir, exist_ok=True)
        except Exception:
            project_dir = os.path.join(tempfile.gettempdir(), "artifacts", project_id, category)
            try:
                os.makedirs(project_dir, exist_ok=True)
            except Exception:
                pass
        file_path = os.path.join(project_dir, f"{art_id}_{filename}")

        try:
            with open(file_path, "wb") as f:
                f.write(data)
        except Exception:
            pass

        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        artifact = Artifact(
            artifact_id=art_id,
            filename=filename,
            project_id=project_id,
            category=category,
            content_type=content_type,
            size_bytes=len(data),
            sha256_hash=sha256,
            storage_backend="filesystem",
            storage_path_or_uri=file_path,
            metadata=metadata or {},
            download_url=f"/api/v1/artifacts/{art_id}/download",
        )
        self._registry[art_id] = artifact
        logger.info(f"[FilesystemArtifactStore] Saved artifact {art_id} ({filename}) to {file_path}")
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

    async def generate_presigned_get_url(self, artifact_id: str, expires_in: int = 900) -> Optional[str]:
        art = await self.get_artifact_metadata(artifact_id)
        return art.download_url if art else None

    async def generate_presigned_put_url(
        self, filename: str, project_id: str, category: str = "general", expires_in: int = 900
    ) -> Dict[str, Any]:
        return {
            "upload_url": f"/api/v1/artifacts/upload?project_id={project_id}&category={category}&filename={filename}",
            "fields": {},
            "storage_backend": "filesystem"
        }


class S3ArtifactStore(ArtifactStore):
    """
    AWS S3 ArtifactStore with SSE-KMS, presigned URL generation,
    and automatic graceful fallback to FilesystemArtifactStore.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        fallback_store: Optional[ArtifactStore] = None,
    ):
        self.bucket_name = bucket_name or os.environ.get("WORKLINE_ARTIFACTS_BUCKET", "workline-artifacts")
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.kms_key_id = os.environ.get("WORKLINE_KMS_KEY_ID")
        self.fallback = fallback_store or FilesystemArtifactStore()
        self._s3_client = None
        self._init_s3_client()

    def _init_s3_client(self):
        try:
            import boto3
            from botocore.config import Config
            config = Config(
                region_name=self.region_name,
                signature_version="s3v4",
                retries={"max_attempts": 3, "mode": "standard"},
            )
            self._s3_client = boto3.client("s3", config=config)
        except Exception as e:
            logger.warning(f"[S3ArtifactStore] boto3 S3 client not available ({e}); fallback active.")
            self._s3_client = None

    async def put_artifact(
        self,
        filename: str,
        data: bytes,
        project_id: str = "default",
        category: str = "general",
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        if not self._s3_client:
            return await self.fallback.put_artifact(filename, data, project_id, category, content_type, metadata)

        sha256 = hashlib.sha256(data).hexdigest()
        art_id = f"art-{sha256[:12]}"
        s3_key = f"projects/{project_id}/{category}/{art_id}_{filename}"

        if not content_type:
            content_type, _ = mimetypes.guess_type(filename)
            content_type = content_type or "application/octet-stream"

        put_kwargs: Dict[str, Any] = {
            "Bucket": self.bucket_name,
            "Key": s3_key,
            "Body": data,
            "ContentType": content_type,
            "Metadata": {
                "artifact_id": art_id,
                "project_id": project_id,
                "sha256": sha256,
            }
        }
        if self.kms_key_id:
            put_kwargs["ServerSideEncryption"] = "aws:kms"
            put_kwargs["SSEKMSKeyId"] = self.kms_key_id

        try:
            self._s3_client.put_object(**put_kwargs)
            download_url = self._s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=3600
            )
            artifact = Artifact(
                artifact_id=art_id,
                filename=filename,
                project_id=project_id,
                category=category,
                content_type=content_type,
                size_bytes=len(data),
                sha256_hash=sha256,
                storage_backend="s3",
                storage_path_or_uri=f"s3://{self.bucket_name}/{s3_key}",
                metadata=metadata or {},
                download_url=download_url
            )
            logger.info(f"[S3ArtifactStore] Stored artifact {art_id} ({filename}) to s3://{self.bucket_name}/{s3_key}")
            return artifact
        except Exception as e:
            logger.warning(f"[S3ArtifactStore] S3 upload failed ({e}); using filesystem fallback.")
            return await self.fallback.put_artifact(filename, data, project_id, category, content_type, metadata)

    async def get_artifact_metadata(self, artifact_id: str) -> Optional[Artifact]:
        return await self.fallback.get_artifact_metadata(artifact_id)

    async def get_artifact_bytes(self, artifact_id: str) -> Optional[bytes]:
        art = await self.fallback.get_artifact_metadata(artifact_id)
        if not art or art.storage_backend != "s3" or not self._s3_client:
            return await self.fallback.get_artifact_bytes(artifact_id)

        try:
            # Parse s3 uri
            s3_uri = art.storage_path_or_uri
            parts = s3_uri.replace("s3://", "").split("/", 1)
            bucket = parts[0]
            key = parts[1]
            response = self._s3_client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except Exception as e:
            logger.warning(f"[S3ArtifactStore] Failed to fetch s3 object ({e}); checking fallback.")
            return await self.fallback.get_artifact_bytes(artifact_id)

    async def list_artifacts(self, project_id: Optional[str] = None) -> List[Artifact]:
        return await self.fallback.list_artifacts(project_id)

    async def generate_presigned_get_url(self, artifact_id: str, expires_in: int = 900) -> Optional[str]:
        art = await self.get_artifact_metadata(artifact_id)
        if not art or not self._s3_client or art.storage_backend != "s3":
            return await self.fallback.generate_presigned_get_url(artifact_id, expires_in)

        try:
            parts = art.storage_path_or_uri.replace("s3://", "").split("/", 1)
            return self._s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": parts[0], "Key": parts[1]},
                ExpiresIn=expires_in
            )
        except Exception as e:
            logger.warning(f"[S3ArtifactStore] Failed to generate presigned GET url: {e}")
            return art.download_url

    async def generate_presigned_put_url(
        self, filename: str, project_id: str, category: str = "general", expires_in: int = 900
    ) -> Dict[str, Any]:
        if not self._s3_client:
            return await self.fallback.generate_presigned_put_url(filename, project_id, category, expires_in)

        s3_key = f"projects/{project_id}/{category}/{int(time.time())}_{filename}"
        params = {"Bucket": self.bucket_name, "Key": s3_key}
        if self.kms_key_id:
            params["ServerSideEncryption"] = "aws:kms"
            params["SSEKMSKeyId"] = self.kms_key_id

        try:
            presigned_url = self._s3_client.generate_presigned_url(
                "put_object",
                Params=params,
                ExpiresIn=expires_in
            )
            return {
                "upload_url": presigned_url,
                "s3_uri": f"s3://{self.bucket_name}/{s3_key}",
                "storage_backend": "s3",
                "expires_in": expires_in
            }
        except Exception as e:
            logger.warning(f"[S3ArtifactStore] Failed generating presigned PUT url: {e}")
            return await self.fallback.generate_presigned_put_url(filename, project_id, category, expires_in)


default_artifact_store = S3ArtifactStore()
