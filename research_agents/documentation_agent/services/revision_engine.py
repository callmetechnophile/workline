"""
Revision Engine — controls document lifecycle status transitions.
Self-approval is blocked. ArmorIQ authorization checked externally.
"""

from datetime import datetime, timezone
from typing import Optional

from research_agents.documentation_agent.schemas import (
    DocumentRecord, DocumentStatus, RevisionEntry,
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


ALLOWED_TRANSITIONS = {
    DocumentStatus.DRAFT:                   [DocumentStatus.IN_REVIEW, DocumentStatus.WITHDRAWN],
    DocumentStatus.IN_REVIEW:              [DocumentStatus.APPROVED, DocumentStatus.REVIEW_CHANGES_REQUIRED, DocumentStatus.WITHDRAWN],
    DocumentStatus.REVIEW_CHANGES_REQUIRED: [DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW, DocumentStatus.WITHDRAWN],
    DocumentStatus.APPROVED:               [DocumentStatus.PUBLISHED, DocumentStatus.WITHDRAWN],
    DocumentStatus.PUBLISHED:              [DocumentStatus.SUPERSEDED, DocumentStatus.WITHDRAWN],
    DocumentStatus.SUPERSEDED:             [DocumentStatus.ARCHIVED],
    DocumentStatus.WITHDRAWN:              [DocumentStatus.ARCHIVED],
    DocumentStatus.ARCHIVED:               [],
}


class RevisionEngine:

    def transition(
        self,
        doc: DocumentRecord,
        target_status: DocumentStatus,
        actor: str,
        change_summary: str,
        approver: Optional[str] = None,
    ) -> tuple[DocumentRecord, Optional[str]]:
        """
        Attempt a status transition. Returns (updated_doc, error_string).
        Error is None on success.
        """
        allowed = ALLOWED_TRANSITIONS.get(doc.status, [])
        if target_status not in allowed:
            return doc, f"INVALID_TRANSITION: {doc.status.value} → {target_status.value}"

        # Block self-approval
        if target_status in (DocumentStatus.APPROVED, DocumentStatus.PUBLISHED):
            if approver and approver == doc.author:
                return doc, "SELF_APPROVAL_DENIED: Author cannot approve their own document."

        doc.status = target_status
        if approver:
            doc.approver = approver

        # Bump revision on approval/publish
        if target_status in (DocumentStatus.APPROVED, DocumentStatus.PUBLISHED):
            try:
                doc.revision = str(int(doc.revision) + 1).zfill(2)
            except ValueError:
                pass

        doc.revision_history.append(RevisionEntry(
            revision_number=doc.revision,
            author=actor,
            timestamp=_utcnow(),
            change_summary=change_summary,
            status=doc.status,
        ))
        return doc, None
