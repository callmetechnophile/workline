"""
Approval policy and self-approval prevention engine for EngineeringChangeControlAgent (Sections 30–33, 77).
"""

from datetime import datetime, timezone
import uuid
from typing import Optional
from research_agents.engineering_change_control.schemas import ApprovalObject, ChangeRequest


class ChangeApprovalEngine:
    """Evaluates approval requirements and validates approver credentials."""

    def create_approval_request(self, change: ChangeRequest) -> Optional[ApprovalObject]:
        if change.severity in ("HIGH", "CRITICAL") or change.change_type in ("ARCHITECTURE_CHANGE", "REQUIREMENT_CHANGE"):
            return ApprovalObject(
                approval_id=f"APPR-{uuid.uuid4().hex[:6].upper()}",
                change_id=change.change_id,
                approval_type="SAFETY_REVIEW" if change.severity == "CRITICAL" else "ENGINEERING_REVIEW",
                requested_from="engineering_lead",
                reason=f"Mandatory review required for {change.severity} {change.change_type}.",
                status="PENDING",
            )
        return None

    def approve_change(
        self,
        approval: ApprovalObject,
        change: ChangeRequest,
        approver_id: str,
    ) -> ApprovalObject:
        # Enforce No Self-Approval Rule (Section 77)
        if approver_id == change.requested_by and change.severity in ("HIGH", "CRITICAL"):
            raise PermissionError(
                f"APPROVAL_DENIED: Requester '{approver_id}' cannot self-approve critical change '{change.change_id}'. Independent review required."
            )

        approval.approved_by = approver_id
        approval.status = "APPROVED"
        approval.resolved_at = datetime.now(timezone.utc).isoformat()
        return approval
