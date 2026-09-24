"""
ProjectRetriever: Core retrieval abstraction for WORKLINE.

Decouples AI agents, LiveKit, and CLI commands from Moss implementation specifics.
Provides hybrid semantic + deterministic search with:

  mode="local"  → always uses LocalMossAdapter (.wl/index/) + filesystem fallback.
                  Fully offline. No backend processes needed.

  mode="stack"  → routes to the live QdrantManager when the stack is running.
                  Falls back to local mode automatically if Qdrant is not up.

  mode="auto"   → (default) tries stack mode first; falls back to local mode.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Literal, Optional, Set

from cli.workline.project.filesystem import discover_project_files
from cli.workline.retrieval.moss_adapter import LocalMossAdapter
from cli.workline.retrieval.parsers import parse_file_into_records
from cli.workline.retrieval.record import EngineeringRecord


# ── Type alias ────────────────────────────────────────────────────────────────
RetrievalMode = Literal["local", "stack", "auto"]


class ProjectRetriever:
    """
    Unified project context retriever.

    The rest of the WORKLINE CLI depends on this interface.
    Combines:
    - Local Moss semantic retrieval (LocalMossAdapter, .wl/index/)
    - Live Qdrant stack retrieval (QdrantManager) when running
    - Deterministic filesystem parameter searches
    - Direct filesystem fallback when index is uninitialized or corrupted

    Parameters
    ----------
    project_root : Path
        The root of the .wl project directory.
    adapter : LocalMossAdapter, optional
        Pre-configured local Moss adapter. Constructed automatically if omitted.
    mode : "local" | "stack" | "auto"
        Retrieval routing mode (default: "auto").
    qdrant_collection : str
        Qdrant collection to query in stack mode (default: workline_documents).
    """

    def __init__(
        self,
        project_root: Path,
        adapter: Optional[LocalMossAdapter] = None,
        mode: RetrievalMode = "auto",
        qdrant_collection: str = "workline_documents",
    ):
        self.project_root = project_root.resolve()
        self.adapter = adapter or LocalMossAdapter(self.project_root)
        self.mode: RetrievalMode = mode
        self.qdrant_collection = qdrant_collection
        self._qdrant_available: Optional[bool] = None  # lazy-checked

    # ── Public API ────────────────────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        resource_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Primary retrieval method.

        Executes hybrid search via the selected retrieval mode with deterministic
        boosting and automatic fallback to local filesystem scan if the index is
        empty or unavailable.
        """
        effective_mode = self._resolve_mode()

        if effective_mode == "stack":
            results = self._stack_retrieve(query, top_k, resource_types, filters)
            if results:
                return self._deduplicate(self._apply_deterministic_boost(query, results), top_k)

        # Local Moss index
        if self.adapter.is_ready:
            results = self._local_moss_retrieve(query, top_k, resource_types, filters)
            if results:
                return self._deduplicate(self._apply_deterministic_boost(query, results), top_k)

        # Final fallback: direct filesystem scan
        return self._filesystem_fallback_search(query, top_k, resource_types, filters)

    def lookup_component(self, mpn_or_name: str) -> Optional[EngineeringRecord]:
        """Direct deterministic lookup for a component by MPN."""
        results = self.retrieve(
            query=mpn_or_name,
            top_k=3,
            resource_types=["component", "bom"],
            filters={"mpn": mpn_or_name},
        )
        return results[0] if results else None

    def lookup_tasks(
        self,
        status: Optional[str] = None,
        assignee: Optional[str] = None,
    ) -> List[EngineeringRecord]:
        """Deterministic query for tasks filtered by status and assignee."""
        filters: Dict[str, Any] = {}
        if status:
            filters["status"] = status
        if assignee:
            filters["assignee"] = assignee

        return self.retrieve(
            query=f"task {status or ''} {assignee or ''}".strip(),
            top_k=50,
            resource_types=["task"],
            filters=filters or None,
        )

    @property
    def active_mode(self) -> str:
        """Return the effective retrieval mode currently in use."""
        return self._resolve_mode()

    # ── Internal routing ──────────────────────────────────────────────────────

    def _resolve_mode(self) -> str:
        """Determine the effective retrieval mode."""
        if self.mode == "local":
            return "local"
        if self.mode == "stack":
            return "stack" if self._is_qdrant_available() else "local"
        # "auto" — try stack if available, else local
        return "stack" if self._is_qdrant_available() else "local"

    def _is_qdrant_available(self) -> bool:
        """Lazy TCP check whether Qdrant is reachable."""
        if self._qdrant_available is not None:
            return self._qdrant_available
        import socket
        try:
            with socket.create_connection(("localhost", 6333), timeout=1.5):
                self._qdrant_available = True
        except (socket.timeout, ConnectionRefusedError, OSError):
            self._qdrant_available = False
        return self._qdrant_available

    # ── Stack retrieval (Qdrant) ──────────────────────────────────────────────

    def _stack_retrieve(
        self,
        query: str,
        top_k: int,
        resource_types: Optional[List[str]],
        filters: Optional[Dict[str, Any]],
    ) -> List[EngineeringRecord]:
        """Route to the live QdrantManager when the stack is up."""
        try:
            from backend.workline.retrieval.qdrant import qdrant_manager
            from backend.workline.retrieval.embeddings import get_embedding_provider

            import asyncio
            if not qdrant_manager.is_connected():
                asyncio.run(qdrant_manager.connect())

            provider = get_embedding_provider()
            embedding = provider.embed(query)

            raw_results = asyncio.run(
                qdrant_manager.search(
                    collection_name=self.qdrant_collection,
                    query_vector=embedding,
                    top_k=top_k,
                    filters=filters,
                )
            )

            records: List[EngineeringRecord] = []
            for item in raw_results:
                payload = item.get("payload", {})
                rec = EngineeringRecord(
                    record_id=str(item.get("id", "")),
                    resource_type=str(payload.get("resource_type", "document")),
                    title=str(payload.get("title", "")),
                    content=str(payload.get("content", "")),
                    source_path=str(payload.get("source_path", "")),
                    score=float(item.get("score", 0.0)),
                    metadata=payload,
                )
                if resource_types:
                    if rec.resource_type.lower() not in [r.lower() for r in resource_types]:
                        continue
                records.append(rec)

            return records

        except Exception:
            # Any failure falls through to local mode
            self._qdrant_available = False
            return []

    # ── Local Moss retrieval ──────────────────────────────────────────────────

    def _local_moss_retrieve(
        self,
        query: str,
        top_k: int,
        resource_types: Optional[List[str]],
        filters: Optional[Dict[str, Any]],
    ) -> List[EngineeringRecord]:
        """Retrieve from the local Moss index."""
        results: List[EngineeringRecord] = []
        if resource_types:
            for rtype in resource_types:
                res = self.adapter.search(
                    query=query,
                    top_k=top_k,
                    resource_type=rtype,
                    metadata_filters=filters,
                )
                results.extend(res)
        else:
            results = self.adapter.search(
                query=query,
                top_k=top_k,
                resource_type=None,
                metadata_filters=filters,
            )
        return results

    # ── Deterministic boosting ────────────────────────────────────────────────

    def _apply_deterministic_boost(
        self,
        query: str,
        records: List[EngineeringRecord],
    ) -> List[EngineeringRecord]:
        """Boost score for exact MPN, title, or ID matches in query."""
        q_clean = query.strip().lower()
        for r in records:
            mpn = str(r.metadata.get("mpn", "")).lower()
            if mpn and (mpn in q_clean or q_clean in mpn):
                r.score = max(r.score, 0.98)
            if r.title and q_clean in r.title.lower():
                r.score = max(r.score, 0.95)
            rid = str(
                r.metadata.get("requirement_id")
                or r.metadata.get("decision_id")
                or r.metadata.get("task_id", "")
            ).lower()
            if rid and rid in q_clean:
                r.score = max(r.score, 0.99)
        return records

    # ── Deduplication ─────────────────────────────────────────────────────────

    def _deduplicate(
        self,
        results: List[EngineeringRecord],
        top_k: int,
    ) -> List[EngineeringRecord]:
        """Deduplicate by record_id and return top-k by score."""
        seen_ids: Set[str] = set()
        deduped: List[EngineeringRecord] = []
        for r in sorted(results, key=lambda x: x.score, reverse=True):
            if r.record_id not in seen_ids:
                seen_ids.add(r.record_id)
                deduped.append(r)
        return deduped[:top_k]

    # ── Filesystem fallback ───────────────────────────────────────────────────

    def _filesystem_fallback_search(
        self,
        query: str,
        top_k: int = 10,
        resource_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Direct filesystem search fallback when no index is available.
        Ensures the CLI remains fully functional offline without any backend.
        """
        discovered = discover_project_files(self.project_root)
        q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) >= 2]

        candidates: List[EngineeringRecord] = []
        for rel_posix, abs_path in discovered.items():
            records = parse_file_into_records(abs_path, rel_posix, "PROJ-FALLBACK")
            for rec in records:
                if resource_types and rec.resource_type.lower() not in [
                    r.lower() for r in resource_types
                ]:
                    continue
                if filters:
                    match = True
                    for fk, fv in filters.items():
                        if str(rec.metadata.get(fk, "")).lower() != str(fv).lower():
                            match = False
                            break
                    if not match:
                        continue

                # Score based on token containment
                text_lower = f"{rec.title} {rec.content} {rec.metadata}".lower()
                hits = sum(1 for t in q_tokens if t in text_lower)
                if hits > 0:
                    rec.score = round(hits / (len(q_tokens) or 1.0), 3)
                    candidates.append(rec)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]
