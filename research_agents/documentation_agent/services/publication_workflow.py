"""
Publication Workflow — orchestrates document approval and controlled publication.
Controlled publication requires ArmorIQ authorization (checked externally).
Agent #27 cannot self-approve documents.
"""

from typing import Optional, Tuple

from research_agents.documentation_agent.schemas import (
    DocumentRecord, DocumentStatus, PublicationChannel,
)
from research_agents.documentation_agent.services.revision_engine import RevisionEngine


class PublicationWorkflow:

    def __init__(self):
        self._revision = RevisionEngine()

    def submit_for_review(
        self, doc: DocumentRecord, actor: str
    ) -> Tuple[DocumentRecord, Optional[str]]:
        return self._revision.transition(
            doc, DocumentStatus.IN_REVIEW, actor, "Submitted for review."
        )

    def request_changes(
        self, doc: DocumentRecord, actor: str, reason: str
    ) -> Tuple[DocumentRecord, Optional[str]]:
        doc_out, err = self._revision.transition(
            doc, DocumentStatus.REVIEW_CHANGES_REQUIRED, actor, f"Changes requested: {reason}"
        )
        return doc_out, err

    def approve(
        self, doc: DocumentRecord, approver: str
    ) -> Tuple[DocumentRecord, Optional[str]]:
        """Approve a document. Approver CANNOT be the same as the author."""
        return self._revision.transition(
            doc, DocumentStatus.APPROVED, approver,
            "Document approved for publication.",
            approver=approver,
        )

    def publish(
        self,
        doc: DocumentRecord,
        publisher: str,
        channel: PublicationChannel,
        armoriq_authorized: bool,
    ) -> Tuple[DocumentRecord, Optional[str]]:
        """Publish document. Controlled channels require ArmorIQ authorization."""
        if channel in (
            PublicationChannel.CONTROLLED_VAULT,
            PublicationChannel.EXTERNAL_RELEASE,
            PublicationChannel.REGULATORY_SUBMISSION,
        ) and not armoriq_authorized:
            return doc, f"ARMORIQ_AUTHORIZATION_REQUIRED: Publication to {channel.value} denied."

        return self._revision.transition(
            doc, DocumentStatus.PUBLISHED, publisher,
            f"Published to {channel.value}.",
            approver=doc.approver,
        )

    def withdraw(
        self, doc: DocumentRecord, actor: str, reason: str
    ) -> Tuple[DocumentRecord, Optional[str]]:
        return self._revision.transition(
            doc, DocumentStatus.WITHDRAWN, actor, f"Withdrawn: {reason}"
        )
