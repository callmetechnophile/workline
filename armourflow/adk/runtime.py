"""Google ADK Runtime integration layer."""

from typing import Any, Dict, Optional
from armourflow.adk.adapter import ADKControlFabricAdapter
from armourflow.config.settings import PlatformSettings, get_settings


class GoogleADKRuntime:
    """
    Centralized Google ADK Runtime managing session lifecycles,
    dispatching work strictly via the Control Fabric Adapter.
    """

    _instance: Optional["GoogleADKRuntime"] = None

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.adapter = ADKControlFabricAdapter()
        self.runtime_id = self.settings.adk_runtime
        self.enabled = self.settings.adk_enabled

    @classmethod
    def get_instance(cls) -> "GoogleADKRuntime":
        if cls._instance is None:
            cls._instance = GoogleADKRuntime()
        return cls._instance

    async def run(
        self,
        task_name: str,
        parameters: Dict[str, Any],
        project_id: str = "default",
        agent_id: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Dispatch task through ADK-Fabric pipeline."""
        if not self.enabled:
            return {"adk_status": "DISABLED", "error": "Google ADK Runtime is disabled by configuration."}

        return await self.adapter.execute_adk_task(
            task_name=task_name,
            parameters=parameters,
            project_id=project_id,
            agent_id=agent_id,
            capability=capability,
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.enabled else "DISABLED",
            "component": "GoogleADKRuntime",
            "runtime_id": self.runtime_id,
            "enabled": self.enabled,
        }


def get_adk_runtime() -> GoogleADKRuntime:
    return GoogleADKRuntime.get_instance()
