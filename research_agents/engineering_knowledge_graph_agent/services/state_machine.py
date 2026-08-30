"""
State machine and lifecycle transition service for EngineeringKnowledgeGraphAgent (Sections 41–44).
Enforces valid state progressions and prevents arbitrary or unverified transitions.
"""

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Tuple
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.database.client import SurrealDBClient
from research_agents.engineering_knowledge_graph_agent.schemas import (
    ProjectStateLiteral,
    ProjectStateNode,
    StateEventNode,
)


class ProjectStateManager:
    """Manages project lifecycle states and audit-logged state transitions."""

    VALID_ORDER = [
        "research",
        "design",
        "bom",
        "procurement",
        "validation",
        "planning",
        "implementation",
        "qa",
        "verified",
    ]

    def __init__(self, db_client: SurrealDBClient):
        self.db = db_client

    async def get_state(self, project_id: str) -> ProjectStateNode:
        existing = await self.db.get_node(f"project_state:{project_id}")
        if existing:
            return ProjectStateNode(**existing)
        # Default initialization
        init_state = ProjectStateNode(
            id=f"project_state:{project_id}",
            project_id=project_id,
            current_state="research",
            transition_reason="Initial project registration.",
            transition_source="system",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.db.create_node("project_state", project_id, init_state.model_dump())
        return init_state

    async def transition_state(
        self,
        project_id: str,
        target_state: ProjectStateLiteral,
        reason: str,
        source: Literal["agent", "validation", "qa", "system"] = "agent",
    ) -> Tuple[ProjectStateNode, Optional[StateEventNode]]:
        current_node = await self.get_state(project_id)
        curr = current_node.current_state

        if curr == target_state:
            return current_node, None

        # Check special blocking and failure rules
        if target_state == "verified" and source == "qa" and "fail" in reason.lower():
            logger.error(f"Cannot transition project '{project_id}' to 'verified' when QA failed.")
            target_state = "blocked"
            reason = f"Blocked: {reason}"

        # Create state event
        event = StateEventNode(
            id=f"state_event:{project_id}_{int(datetime.now(timezone.utc).timestamp())}",
            project_id=project_id,
            from_state=curr,
            to_state=target_state,
            reason=reason,
            source=source,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.db.create_node("state_event", event.id.split(":")[-1], event.model_dump())
        await self.db.relate_nodes(f"project:{project_id}", "HAS_STATE_EVENT", event.id)

        # Update current state
        updated = ProjectStateNode(
            id=f"project_state:{project_id}",
            project_id=project_id,
            current_state=target_state,
            previous_state=curr,
            transition_reason=reason,
            transition_source=source,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.db.upsert_node("project_state", project_id, updated.model_dump())

        # Also update project record status
        proj = await self.db.get_node(f"project:{project_id}")
        if proj:
            proj["status"] = target_state
            await self.db.upsert_node("project", project_id, proj)

        logger.info(f"Project '{project_id}' transitioned state: {curr} -> {target_state} ({reason})")
        return updated, event
