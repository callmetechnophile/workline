"""
Audit trail aggregation service for EngineeringExecutionAgent (Section 53).
"""

from typing import List
from research_agents.engineering_execution_agent.schemas import ExecutionAuditItem


class AuditService:
    """Aggregates and formats cryptographic execution audit records."""

    def filter_audit_trail(
        self,
        audit_items: List[ExecutionAuditItem],
        status_filter: str = None,
    ) -> List[ExecutionAuditItem]:
        if not status_filter:
            return audit_items
        return [item for item in audit_items if item.status == status_filter]
