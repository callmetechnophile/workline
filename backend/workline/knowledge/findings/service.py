"""Engineering Finding management service."""

from datetime import datetime, timezone
import logging
import threading
from typing import Dict, List, Optional

from backend.workline.knowledge.models import (
    Actor,
    EngineeringFinding,
    FindingSeverity,
    FindingStatus,
    KnowledgeAuditEvent,
    KnowledgeAuditEventType,
)

logger = logging.getLogger("workline.knowledge.findings")


class FindingService:
    """Manages engineering findings, failure investigations, and resolution linkages."""

    def __init__(self):
        self._lock = threading.RLock()
        self._findings: Dict[str, EngineeringFinding] = {}  # finding_id -> EngineeringFinding
        self._audit_logs: List[KnowledgeAuditEvent] = []

    def create_finding(
        self,
        finding: EngineeringFinding,
        actor: Optional[Actor] = None,
    ) -> EngineeringFinding:
        """Records an engineering finding or validation failure."""
        with self._lock:
            now_iso = datetime.now(timezone.utc).isoformat()
            finding.created_at = now_iso
            if actor:
                finding.created_by = actor

            self._findings[finding.finding_id] = finding

            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{finding.finding_id}_created",
                    event_type=KnowledgeAuditEventType.FINDING_CREATED,
                    project_id=finding.project_id,
                    object_id=finding.finding_id,
                    actor=finding.created_by,
                    details={"severity": finding.severity.value, "category": finding.category},
                )
            )
            return finding

    def resolve_finding(
        self,
        finding_id: str,
        resolution: str,
        resolved_by_decision_id: Optional[str] = None,
        actor: Optional[Actor] = None,
    ) -> EngineeringFinding:
        """Marks a finding resolved and optionally links it to a corrective decision."""
        with self._lock:
            finding = self._findings.get(finding_id)
            if not finding:
                raise ValueError(f"Finding '{finding_id}' not found.")

            finding.status = FindingStatus.RESOLVED
            finding.resolution = resolution
            if resolved_by_decision_id:
                finding.resolved_by_decision_id = resolved_by_decision_id

            current_actor = actor or finding.created_by
            self._audit_logs.append(
                KnowledgeAuditEvent(
                    event_id=f"evt_{finding_id}_resolved",
                    event_type=KnowledgeAuditEventType.FINDING_RESOLVED,
                    project_id=finding.project_id,
                    object_id=finding_id,
                    actor=current_actor,
                    details={"resolution": resolution, "decision_id": resolved_by_decision_id},
                )
            )
            return finding

    def get_finding(self, finding_id: str) -> Optional[EngineeringFinding]:
        """Retrieves a single finding."""
        with self._lock:
            return self._findings.get(finding_id)

    def list_findings(
        self,
        project_id: str,
        category: Optional[str] = None,
        status: Optional[FindingStatus] = None,
    ) -> List[EngineeringFinding]:
        """Lists findings for a project."""
        with self._lock:
            res = [f for f in self._findings.values() if f.project_id == project_id]
            if category:
                res = [f for f in res if f.category == category]
            if status:
                res = [f for f in res if f.status == status]
            return sorted(res, key=lambda f: f.created_at)


finding_service = FindingService()
