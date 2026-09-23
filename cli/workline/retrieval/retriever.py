"""
ProjectRetriever: Core retrieval abstraction for WORKLINE.
Decouples AI agents, LiveKit, and CLI commands from Moss implementation specifics.
Provides hybrid semantic + deterministic search with automatic filesystem fallback.
"""

from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Set

from cli.workline.project.filesystem import discover_project_files
from cli.workline.retrieval.moss_adapter import LocalMossAdapter
from cli.workline.retrieval.parsers import parse_file_into_records
from cli.workline.retrieval.record import EngineeringRecord


class ProjectRetriever:
    """
    Unified project context retriever.
    The rest of WORKLINE depends on this interface.
    Combines:
    - Local Moss semantic retrieval
    - Deterministic filesystem parameter searches
    - Direct filesystem fallback when index is uninitialized or corrupted
    """

    def __init__(self, project_root: Path, adapter: Optional[LocalMossAdapter] = None):
        self.project_root = project_root.resolve()
        self.adapter = adapter or LocalMossAdapter(self.project_root)

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        resource_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Primary retrieval method.
        Executes hybrid search via LocalMossAdapter with deterministic boosting
        and automatic fallback to local filesystem scan if index is empty.
        """
        # If the local Moss index is ready, use it
        if self.adapter.is_ready:
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
                
            # Perform deterministic boosting for exact MPN or identifier match
            results = self._apply_deterministic_boost(query, results)
            # Deduplicate by record_id and sort by score
            seen_ids: Set[str] = set()
            deduped = []
            for r in sorted(results, key=lambda x: x.score, reverse=True):
                if r.record_id not in seen_ids:
                    seen_ids.add(r.record_id)
                    deduped.append(r)
            if deduped:
                return deduped[:top_k]

        # Fallback: Deterministic scan over project filesystem
        return self._filesystem_fallback_search(query, top_k, resource_types, filters)

    def _apply_deterministic_boost(
        self,
        query: str,
        records: List[EngineeringRecord],
    ) -> List[EngineeringRecord]:
        """Boost score if record has exact match for query terms in MPN, title, or ID."""
        q_clean = query.strip().lower()
        for r in records:
            # Check MPN exact match
            mpn = str(r.metadata.get("mpn", "")).lower()
            if mpn and (mpn in q_clean or q_clean in mpn):
                r.score = max(r.score, 0.98)
            # Check Title exact match
            if r.title and q_clean in r.title.lower():
                r.score = max(r.score, 0.95)
            # Check Resource ID
            rid = str(r.metadata.get("requirement_id") or r.metadata.get("decision_id") or r.metadata.get("task_id", "")).lower()
            if rid and rid in q_clean:
                r.score = max(r.score, 0.99)
        return records

    def _filesystem_fallback_search(
        self,
        query: str,
        top_k: int = 10,
        resource_types: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[EngineeringRecord]:
        """
        Direct filesystem search fallback when Moss index is not loaded.
        Ensures the CLI remains fully functional without an index.
        """
        discovered = discover_project_files(self.project_root)
        q_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) >= 2]
        
        candidates: List[EngineeringRecord] = []
        for rel_posix, abs_path in discovered.items():
            records = parse_file_into_records(abs_path, rel_posix, "PROJ-FALLBACK")
            for rec in records:
                if resource_types and rec.resource_type.lower() not in [r.lower() for r in resource_types]:
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
                matches = sum(1 for t in q_tokens if t in text_lower)
                if matches > 0:
                    rec.score = round(matches / (len(q_tokens) or 1.0), 3)
                    candidates.append(rec)

        candidates.sort(key=lambda x: x.score, reverse=True)
        return candidates[:top_k]

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
        filters = {}
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
