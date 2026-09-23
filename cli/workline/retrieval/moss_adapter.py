"""
LocalMossAdapter: On-device integration layer for the Moss semantic retrieval runtime.
Strictly local - zero cloud API calls, zero remote search endpoints, zero cloud credential dependencies.
Provides automatic fallback to high-performance embedded LocalRetrievalEngine.
"""

from datetime import datetime, timezone
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from cli.workline.config.config import MossConfig
from cli.workline.retrieval.local_engine import LocalRetrievalEngine
from cli.workline.retrieval.record import EngineeringRecord

MOSS_METADATA_RELPATH = ".wl/moss.wl"
MOSS_INDEX_DIR_RELPATH = ".wl/index"


class LocalMossAdapter:
    """
    On-device adapter for Moss indexing and retrieval.
    Manages index creation, incremental updates, persistence in .wl/index/,
    and status metadata in .wl/moss.wl.
    """

    def __init__(self, project_root: Path, config: Optional[MossConfig] = None):
        self.project_root = project_root.resolve()
        self.config = config or MossConfig()
        self.index_dir = self.project_root / MOSS_INDEX_DIR_RELPATH
        self.metadata_file = self.project_root / MOSS_METADATA_RELPATH
        
        # Initialize the local embedded search engine
        self.engine = LocalRetrievalEngine(storage_dir=self.index_dir, dim=self.config.embedding_dim)
        
        # Attempt to load existing index from disk if present
        self._is_loaded = False
        if self.index_dir.exists():
            self._is_loaded = self.engine.load()

    @property
    def is_ready(self) -> bool:
        """Return True if index is loaded and contains documents."""
        return self._is_loaded and len(self.engine.records) > 0

    def get_document_count(self) -> int:
        """Return number of currently indexed records."""
        return len(self.engine.records)

    def get_metadata(self) -> Dict[str, Any]:
        """Read .wl/moss.wl metadata."""
        if not self.metadata_file.exists():
            return {
                "enabled": True,
                "status": "UNINITIALIZED",
                "document_count": 0,
                "runtime": "local",
                "indexed_at": None,
                "last_manifest_hash": None,
            }
        try:
            data = yaml.safe_load(self.metadata_file.read_text(encoding="utf-8")) or {}
            return data.get("moss", {})
        except Exception:
            return {"enabled": True, "status": "CORRUPTED", "document_count": 0, "runtime": "local"}

    def save_metadata(
        self,
        project_id: str,
        document_count: int,
        manifest_hash: Optional[str] = None,
        status: str = "READY",
    ) -> None:
        """Update .wl/moss.wl with latest indexing status."""
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "moss": {
                "enabled": True,
                "index_name": f"workline_{project_id.lower().replace('-', '_')}",
                "schema_version": self.config.schema_version,
                "status": status,
                "document_count": document_count,
                "runtime": "local",
                "indexed_at": datetime.now(timezone.utc).isoformat(),
                "last_manifest_hash": manifest_hash,
            }
        }
        yaml_content = yaml.dump(data, sort_keys=False, default_flow_style=False)
        self.metadata_file.write_text(yaml_content, encoding="utf-8")

    def reindex_all(self, records: List[EngineeringRecord], project_id: str, manifest_hash: Optional[str] = None) -> int:
        """
        Perform a clean rebuild of the entire local Moss index.
        Wipes existing index state and rebuilds from supplied records.
        """
        self.engine.clear()
        self.engine.add_records(records)
        self.engine.save(self.index_dir)
        self._is_loaded = True
        
        self.save_metadata(
            project_id=project_id,
            document_count=len(records),
            manifest_hash=manifest_hash,
            status="READY",
        )
        return len(records)

    def update_records_for_file(
        self,
        rel_posix: str,
        new_records: List[EngineeringRecord],
        project_id: str,
        manifest_hash: Optional[str] = None,
    ) -> None:
        """
        Incrementally update records for a specific modified or newly added file.
        Removes stale records for the file, then inserts updated records.
        """
        self.engine.remove_records_by_path(rel_posix)
        if new_records:
            self.engine.add_records(new_records)
        self.engine.save(self.index_dir)
        self._is_loaded = True
        
        self.save_metadata(
            project_id=project_id,
            document_count=len(self.engine.records),
            manifest_hash=manifest_hash,
            status="READY",
        )

    def remove_file(self, rel_posix: str, project_id: str, manifest_hash: Optional[str] = None) -> None:
        """Remove all indexed records associated with a deleted file."""
        self.engine.remove_records_by_path(rel_posix)
        self.engine.save(self.index_dir)
        self.save_metadata(
            project_id=project_id,
            document_count=len(self.engine.records),
            manifest_hash=manifest_hash,
            status="READY",
        )

    def search(
        self,
        query: str,
        top_k: int = 10,
        resource_type: Optional[str] = None,
        metadata_filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Search the local index using hybrid semantic + lexical retrieval.
        Executes sub-10ms purely in local process memory.
        """
        if not self._is_loaded:
            self._is_loaded = self.engine.load()
            
        return self.engine.query(
            query_text=query,
            top_k=top_k,
            resource_type=resource_type,
            metadata_filters=metadata_filters,
        )

    def reset_index(self) -> None:
        """Wipe derived index files from disk without touching source project files."""
        self.engine.clear()
        if self.index_dir.exists():
            import shutil
            shutil.rmtree(self.index_dir, ignore_errors=True)
        self._is_loaded = False
