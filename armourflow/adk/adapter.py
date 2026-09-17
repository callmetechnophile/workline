"""Google ADK to Control Fabric Adapter translating requests and responses."""

from typing import Any, Dict, Optional
from armourflow.fabric.fabric import AgentControlFabric, get_control_fabric
from armourflow.fabric.schemas import FabricTask, TaskState


class ADKControlFabricAdapter:
    """
    Translates Google ADK session/task requests into Control Fabric tasks,
    and converts Control Fabric results into ADK-compliant responses.
    """

    def __init__(self, fabric: Optional[AgentControlFabric] = None):
        self.fabric = fabric or get_control_fabric()

    async def execute_adk_task(
        self,
        task_name: str,
        parameters: Dict[str, Any],
        project_id: str = "default",
        user_id: str = "adk_operator",
        agent_id: Optional[str] = None,
        capability: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Translates ADK task invocation -> Control Fabric execution -> ADK response envelope.
        """
        payload = dict(parameters)
        payload["operation"] = task_name
        if session_id:
            payload["session_id"] = session_id

        # Submit task through Control Fabric
        fabric_task: FabricTask = await self.fabric.submit_task(
            payload=payload,
            target_agent_id=agent_id,
            target_capability=capability,
            project_id=project_id,
            user_id=user_id,
        )

        # Map to ADK response structure
        is_success = fabric_task.state == TaskState.COMPLETED
        return {
            "adk_status": "SUCCESS" if is_success else "ERROR",
            "task_id": fabric_task.task_id,
            "project_id": project_id,
            "agent_id": fabric_task.target_agent_id,
            "state": fabric_task.state.value,
            "result": fabric_task.result if is_success else None,
            "error": fabric_task.error,
            "context": fabric_task.context.model_dump(),
        }
