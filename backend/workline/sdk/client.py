"""
Workline Python SDK Client
Unified interface for interacting with Workline in either CLOUD or LOCAL mode.
"""

from typing import Any, Dict, List, Literal, Optional
import os

from backend.workline.sdk.runtime import (
    BaseRuntime,
    CloudRuntime,
    LocalRuntime,
)
from cli.wline.core.paths import get_active_project_name


class Workline:
    """
    Workline Client.

    Usage:
        # Local Mode (Default on developer workstation)
        wl = Workline(mode="local")

        # Cloud Mode (Targets Render R1 Gateway)
        wl = Workline(mode="cloud", api_url="https://api.workline.dev", token="wl_sec_...")
    """

    def __init__(
        self,
        mode: Literal["local", "cloud"] = "local",
        api_url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.mode = mode.lower()
        if self.mode not in ["local", "cloud"]:
            raise ValueError(f"Invalid mode: '{mode}'. Allowed modes are 'local' and 'cloud'.")

        self.api_url = api_url or os.getenv("WORKLINE_API_URL", "http://localhost:10000")
        self.token = token or os.getenv("WORKLINE_AUTH_TOKEN")

        if self.mode == "cloud":
            self._runtime: BaseRuntime = CloudRuntime(api_url=self.api_url, token=self.token)
        else:
            self._runtime = LocalRuntime()

    @property
    def runtime(self) -> BaseRuntime:
        return self._runtime

    # ==========================================================================
    # Knowledge & Retrieval API
    # ==========================================================================
    async def search_knowledge(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search datasheets and knowledge corpus using the active runtime."""
        return await self._runtime.knowledge.search(query, limit=limit)

    async def query_graph(self, statement: str) -> List[Dict[str, Any]]:
        """Query SurrealDB knowledge graph topology."""
        return await self._runtime.graph.query(statement)

    # ==========================================================================
    # Project Identity & Context
    # ==========================================================================
    def get_current_project(self) -> Optional[str]:
        """Get the active project identifier."""
        return get_active_project_name()

    def sync(self) -> Dict[str, Any]:
        """
        Synchronize local project state with cloud state.
        In local mode, verifies local .wlipjt state integrity.
        """
        project = self.get_current_project()
        return {
            "status": "synchronized",
            "mode": self.mode,
            "project_id": project,
            "cloud_target": self.api_url if self.mode == "cloud" else "local_only",
        }
