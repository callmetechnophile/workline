"""End-to-End Orchestration Test for autonomous-rover project through Google ADK Multi-Agent Engine."""

import asyncio
import pytest
from backend.workline.agents.runtime import WorklineADKRuntime
from backend.workline.agents.shared.state import AgentStatus
from backend.workline.agents.shared.tools import WorklineToolSuite
from backend.workline.database.models import ProjectModel
from backend.workline.database.repositories.graph_repository import GraphRepository
from backend.workline.database.repositories.project_repository import ProjectRepository


def test_e2e_autonomous_rover_orchestration():
    """
    Complete end-to-end integration test of the autonomous-rover project:
    Root -> Planning Tree -> Research Tree -> WAITING_FOR_USER -> START_BUILD -> Builder Tree -> Validated BOM.
    """
    async def _run():
        project_repo = ProjectRepository()
        graph_repo = GraphRepository()

        # 1. Initialize project in SurrealDB
        rover_proj = ProjectModel(
            id="project:autonomous-rover",
            name="autonomous-rover",
            display_name="Autonomous Agricultural Rover",
            description="Design an autonomous agricultural rover using an ESP32 controller, environmental sensors, motor control, and wireless communication.",
            domain="robotics",
        )
        await project_repo.create_project(rover_proj)

        tools = WorklineToolSuite(project_repo=project_repo, graph_repo=graph_repo)
        runtime = WorklineADKRuntime(tools=tools)

        # 2. Trigger Root Agent execution (Phase 1: Planning + Research)
        prompt = "Design an autonomous agricultural rover using an ESP32 controller, environmental sensors, motor control, and wireless communication."
        state = await runtime.start_execution(
            project_id="autonomous-rover",
            task=prompt,
        )

        assert state.status == AgentStatus.WAITING_FOR_USER
        assert state.requires_user_action is True
        assert state.action_prompt is not None

        # Verify planning graph nodes created
        graph_payload = await graph_repo.get_project_graph("autonomous-rover")
        assert len(graph_payload.nodes) >= 1

        # 3. Simulate Human User approving START_BUILD
        final_state = await runtime.submit_human_approval(
            execution_id=state.execution_id,
            decision="START_BUILD",
        )

        assert final_state.status == AgentStatus.COMPLETED
        assert final_state.stage == "hardware_build_complete"
        assert final_state.requires_user_action is False

        # 4. Verify authoritative BOM persisted in SurrealDB project record
        updated_proj = await project_repo.get_project("autonomous-rover")
        assert updated_proj is not None
        assert len(updated_proj.bom) >= 8
        assert any("ESP32" in item.get("component_name", "") for item in updated_proj.bom)

        # 5. Verify graph relationships updated in SurrealDB (CONNECTS_TO, POWERED_BY, SATISFIES)
        full_graph = await graph_repo.get_project_graph("autonomous-rover")
        assert len(full_graph.nodes) >= 5
        assert len(full_graph.edges) >= 5

    asyncio.run(_run())
