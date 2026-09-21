"""
Workline AI — Sensitive Approvals Service.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid
from loguru import logger

from backend.workline.collaboration.approvals.models import (
    ApprovalRequest,
    ApprovalStatus,
    CreateApprovalRequest,
    ResolveApprovalRequest,
)


class ApprovalService:
    """Service managing engineering approval gates."""

    def __init__(self):
        # approval_id -> ApprovalRequest
        self._approvals: Dict[str, ApprovalRequest] = {}

    def create_request(
        self,
        payload: CreateApprovalRequest,
        requester_id: str,
        requester_name: Optional[str] = None,
    ) -> ApprovalRequest:
        """Creates an approval request for a sensitive engineering action."""
        approval_id = f"APPR-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now(timezone.utc).isoformat()

        req = ApprovalRequest(
            id=approval_id,
            project_id=payload.project_id,
            team_id=payload.team_id,
            requester_id=requester_id,
            requester_name=requester_name or requester_id,
            artifact_type=payload.artifact_type,
            artifact_id=payload.artifact_id,
            action=payload.action,
            reason=payload.reason or "",
            diff_summary=payload.diff_summary,
            metadata=payload.metadata or {},
            status=ApprovalStatus.PENDING,
            created_at=now,
        )
        self._approvals[approval_id] = req
        logger.info(
            f"[Approvals] Created approval request {approval_id} for {payload.artifact_type}:{payload.artifact_id} by {requester_id}"
        )
        return req

    def get_request(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Gets approval request by ID."""
        return self._approvals.get(approval_id)

    def list_requests(
        self,
        project_id: Optional[str] = None,
        team_id: Optional[str] = None,
        status: Optional[ApprovalStatus] = None,
        artifact_type: Optional[str] = None,
    ) -> List[ApprovalRequest]:
        """Lists approval requests with optional filtering."""
        results = list(self._approvals.values())
        if project_id:
            results = [r for r in results if r.project_id == project_id]
        if team_id:
            results = [r for r in results if r.team_id == team_id]
        if status:
            results = [r for r in results if r.status == status]
        if artifact_type:
            results = [r for r in results if r.artifact_type == artifact_type]

        results.sort(key=lambda r: r.created_at, reverse=True)
        return results

    def resolve_request(
        self,
        approval_id: str,
        payload: ResolveApprovalRequest,
        approver_id: str,
        approver_name: Optional[str] = None,
    ) -> ApprovalRequest:
        """Approves or rejects an engineering request."""
        req = self._approvals.get(approval_id)
        if not req or req.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request '{approval_id}' not found or already resolved.")

        now = datetime.now(timezone.utc).isoformat()
        req.status = payload.status
        req.approver_id = approver_id
        req.approver_name = approver_name or approver_id
        req.resolved_at = now
        req.resolution_notes = payload.notes or ""

        logger.info(
            f"[Approvals] Resolved approval request {approval_id}: {payload.status.value} by {approver_id}"
        )
        return req


# Global singleton instance
approval_service = ApprovalService()
