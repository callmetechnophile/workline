"""
Human decision and approval manager for ProjectLifecycleOrchestrator (Sections 23–25, 66).
Manages approval requests for material architecture revisions, critical requirement changes, or safety escalations.
"""

from typing import Dict, List, Optional
import uuid
from loguru import logger
from research_agents.project_lifecycle_orchestrator.schemas import HumanRequestObject


class HumanDecisionManager:
    """Manages pending and resolved human approvals."""

    def __init__(self):
        self._requests: Dict[str, HumanRequestObject] = {}

    def create_human_request(
        self,
        project_id: str,
        reason: str,
        requested_decision: str,
        affected_objects: Optional[List[str]] = None,
        risk: str = "High architecture impact or unapproved substitution.",
        options: Optional[List[str]] = None,
        recommended_option: Optional[str] = None,
    ) -> HumanRequestObject:
        req_id = f"REQ-HUMAN-{uuid.uuid4().hex[:6].upper()}"
        req = HumanRequestObject(
            request_id=req_id,
            project_id=project_id,
            reason=reason,
            requested_decision=requested_decision,
            affected_objects=affected_objects or [],
            risk=risk,
            options=options or ["Approve Revision", "Reject Revision", "Request Alternative"],
            recommended_option=recommended_option or "Approve Revision",
            status="pending",
        )
        self._requests[req_id] = req
        logger.info(f"Created Human Approval Request [{req_id}] for project '{project_id}': {reason}")
        return req

    def get_pending_requests(self, project_id: Optional[str] = None) -> List[HumanRequestObject]:
        pending = [r for r in self._requests.values() if r.status == "pending"]
        if project_id:
            pending = [r for r in pending if r.project_id == project_id]
        return pending

    def approve_request(self, request_id: str, user_id: str = "user_001") -> Optional[HumanRequestObject]:
        req = self._requests.get(request_id)
        if not req:
            logger.warning(f"Attempted to approve non-existent request '{request_id}'")
            return None
        req.status = "approved"
        logger.info(f"User '{user_id}' approved Human Request [{request_id}]")
        return req

    def reject_request(self, request_id: str, user_id: str = "user_001") -> Optional[HumanRequestObject]:
        req = self._requests.get(request_id)
        if not req:
            logger.warning(f"Attempted to reject non-existent request '{request_id}'")
            return None
        req.status = "rejected"
        logger.info(f"User '{user_id}' rejected Human Request [{request_id}]")
        return req
