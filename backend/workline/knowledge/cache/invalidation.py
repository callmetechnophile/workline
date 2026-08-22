"""Targeted invalidation manager tracking project and source dependencies."""

import threading
from typing import Dict, List, Set


class InvalidationManager:
    """Maintains reverse indices mapping source IDs and project IDs to cache keys."""

    def __init__(self):
        self._lock = threading.RLock()
        self._source_to_keys: Dict[str, Set[str]] = {}
        self._project_to_keys: Dict[str, Set[str]] = {}

    def track(self, key: str, project_id: str, source_id: str = None) -> None:
        with self._lock:
            if project_id:
                if project_id not in self._project_to_keys:
                    self._project_to_keys[project_id] = set()
                self._project_to_keys[project_id].add(key)

            if source_id:
                if source_id not in self._source_to_keys:
                    self._source_to_keys[source_id] = set()
                self._source_to_keys[source_id].add(key)

    def get_keys_by_source(self, source_id: str) -> List[str]:
        with self._lock:
            return list(self._source_to_keys.get(source_id, set()))

    def get_keys_by_project(self, project_id: str) -> List[str]:
        with self._lock:
            return list(self._project_to_keys.get(project_id, set()))

    def remove_key(self, key: str) -> None:
        with self._lock:
            for s in self._source_to_keys.values():
                s.discard(key)
            for s in self._project_to_keys.values():
                s.discard(key)

    def clear(self) -> None:
        with self._lock:
            self._source_to_keys.clear()
            self._project_to_keys.clear()
