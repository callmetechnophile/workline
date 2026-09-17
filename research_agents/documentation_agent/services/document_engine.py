"""
Document Engine — creates and updates DocumentRecord objects.
LLM generates prose sections; deterministic code assigns all metadata.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from research_agents.documentation_agent.config import REVISION_INITIAL
from research_agents.documentation_agent.schemas import (
    AuthorityLevel, DocumentFreshness, DocumentRecord, DocumentStatus,
    DocumentType, RevisionEntry,
)
from research_agents.documentation_agent.providers.base import BaseDocProvider


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class DocumentEngine:
    """Creates new DocumentRecords and updates existing ones via provider-generated prose."""

    def __init__(self, provider: BaseDocProvider):
        self._provider = provider

    def create(
        self,
        project_id:    str,
        document_type: DocumentType,
        title:         str,
        author:        str,
        section_inputs: Dict[str, Any],
        authority_claim: Optional[str] = None,
    ) -> DocumentRecord:
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        # Validate authority claim — never auto-elevate
        authority = AuthorityLevel.UNKNOWN
        if authority_claim:
            try:
                authority = AuthorityLevel(authority_claim.upper())
            except ValueError:
                authority = AuthorityLevel.UNKNOWN

        # Generate prose sections via LLM (metadata stays deterministic)
        sections: Dict[str, str] = {}
        for section_name, context in section_inputs.items():
            extra = context if isinstance(context, dict) else {"content": str(context)}
            ctx = {
                "document_type": document_type.value,
                "title": title,
                "section": section_name,
                **extra,
            }
            sections[section_name] = self._provider.generate_section(section_name, ctx)


        revision_entry = RevisionEntry(
            revision_number="00",
            author=author,
            timestamp=_utcnow(),
            change_summary="Initial creation.",
            status=DocumentStatus.DRAFT,
        )
        return DocumentRecord(
            doc_id=doc_id,
            project_id=project_id,
            document_type=document_type,
            title=title,
            status=DocumentStatus.DRAFT,
            authority=authority,
            freshness=DocumentFreshness.CURRENT,
            revision=REVISION_INITIAL,
            author=author,
            content_sections=sections,
            revision_history=[revision_entry],
        )

    def update_section(
        self,
        doc: DocumentRecord,
        section_name: str,
        new_inputs: Dict[str, Any],
        author: str,
    ) -> DocumentRecord:
        old_text = doc.content_sections.get(section_name, "")
        ctx = {
            "document_type": doc.document_type.value,
            "title": doc.title,
            "section": section_name,
            **new_inputs,
        }
        new_text = self._provider.generate_section(section_name, ctx)
        change_summary = self._provider.summarize_changes(old_text, new_text)
        doc.content_sections[section_name] = new_text

        # Bump revision deterministically
        try:
            rev_num = int(doc.revision) + 1
            doc.revision = str(rev_num).zfill(2)
        except ValueError:
            doc.revision = "01"

        doc.revision_history.append(RevisionEntry(
            revision_number=doc.revision,
            author=author,
            timestamp=_utcnow(),
            change_summary=change_summary,
            status=doc.status,
        ))
        return doc
