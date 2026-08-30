"""
Audit logging service for EngineeringKnowledgeGraphAgent (Sections 90 & 91).
Records immutable mutation audit trails for all graph writes and relations.
"""

from datetime import datetime, timezone
from typing import List, Literal, Optional
import uuid
from research_agents.engineering_knowledge_graph_agent.schemas import AuditEvent


class GraphAuditLogger:
    """Records audit logs for all graph mutations."""

    def __init__(self):
        self.events: List[AuditEvent] = []

    def record_mutation(
        self,
        project_id: str,
        operation: Literal["create", "update", "upsert", "link"],
        object_type: str,
        object_id: str,
        source_artifact: str = "ingestion",
        status: Literal["success", "failed"] = "success",
    ) -> AuditEvent:
        event = AuditEvent(
            audit_id=f"AUD-GRAPH-{uuid.uuid4().hex[:6].upper()}",
            project_id=project_id,
            agent_id="EngineeringKnowledgeGraphAgent",
            operation=operation,
            object_type=object_type,
            object_id=object_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_artifact=source_artifact,
            status=status,
        )
        self.events.append(event)
        return event

    def get_events(self, project_id: Optional[str] = None) -> List[AuditEvent]:
        if project_id:
            return [e for e in self.events if e.project_id == project_id]
        return list(self.events)
