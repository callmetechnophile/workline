"""
Contradiction Detector — detects conflicts between two DocumentRecords.
Returns CONFLICT_DETECTED; never silently resolves.
"""

import uuid
from typing import List

from research_agents.documentation_agent.schemas import (
    ConflictRecord, ConflictSeverity, DocumentRecord,
)


class ContradictionDetector:

    def detect(self, doc_a: DocumentRecord, doc_b: DocumentRecord) -> List[ConflictRecord]:
        """
        Compare two documents for contradictions.
        Returns a list of ConflictRecord — always CONFLICT_DETECTED (never auto-resolved).
        """
        conflicts: List[ConflictRecord] = []

        # Authority downgrade
        _authority_rank = {
            "AUTHORITATIVE": 6, "VERIFIED": 5, "APPROVED": 4,
            "REFERENCE": 3, "UNVERIFIED": 2, "ASSUMPTION": 1, "DRAFT": 1, "UNKNOWN": 0,
        }
        rank_a = _authority_rank.get(doc_a.authority.value, 0)
        rank_b = _authority_rank.get(doc_b.authority.value, 0)
        if rank_a > 0 and rank_b > 0 and abs(rank_a - rank_b) >= 3:
            conflicts.append(ConflictRecord(
                conflict_id=uuid.uuid4().hex[:8].upper(),
                field="authority",
                doc_a_id=doc_a.doc_id,
                doc_b_id=doc_b.doc_id,
                description=(
                    f"Authority conflict: {doc_a.doc_id} is {doc_a.authority.value} "
                    f"but {doc_b.doc_id} is {doc_b.authority.value} — "
                    f"large discrepancy may indicate version mismatch."
                ),
                severity=ConflictSeverity.MAJOR,
                resolution="CONFLICT_DETECTED",
            ))

        # Same-type, different title (possible duplication)
        if doc_a.document_type == doc_b.document_type and doc_a.title == doc_b.title:
            conflicts.append(ConflictRecord(
                conflict_id=uuid.uuid4().hex[:8].upper(),
                field="document_type+title",
                doc_a_id=doc_a.doc_id,
                doc_b_id=doc_b.doc_id,
                description=(
                    f"Duplicate document: both {doc_a.doc_id} and {doc_b.doc_id} "
                    f"share type={doc_a.document_type.value} and title='{doc_a.title}'."
                ),
                severity=ConflictSeverity.MINOR,
                resolution="CONFLICT_DETECTED",
            ))

        # Shared section with significantly different content length (heuristic proxy)
        shared_sections = set(doc_a.content_sections) & set(doc_b.content_sections)
        for section in shared_sections:
            len_a = len(doc_a.content_sections[section].split())
            len_b = len(doc_b.content_sections[section].split())
            if len_a > 0 and len_b > 0:
                ratio = max(len_a, len_b) / min(len_a, len_b)
                if ratio >= 5.0:
                    conflicts.append(ConflictRecord(
                        conflict_id=uuid.uuid4().hex[:8].upper(),
                        field=f"section:{section}",
                        doc_a_id=doc_a.doc_id,
                        doc_b_id=doc_b.doc_id,
                        description=(
                            f"Section '{section}' length divergence (ratio={ratio:.1f}x) "
                            f"suggests content mismatch between documents."
                        ),
                        severity=ConflictSeverity.MINOR,
                        resolution="CONFLICT_DETECTED",
                    ))

        return conflicts
