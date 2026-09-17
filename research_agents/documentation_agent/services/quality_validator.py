"""
Quality Validator — scores a DocumentRecord and emits QualityFlags.
Never invents thresholds; uses policy constants from config.
"""

from typing import List, Tuple

from research_agents.documentation_agent.config import (
    MIN_QUALITY_SCORE_FOR_APPROVAL,
    MIN_QUALITY_SCORE_FOR_PUBLISH,
    MIN_QUALITY_SCORE_FOR_REVIEW,
)
from research_agents.documentation_agent.schemas import (
    AuthorityLevel, DocumentFreshness, DocumentRecord,
    DocumentStatus, QualityFlag,
)


class QualityValidator:

    def validate(self, doc: DocumentRecord) -> Tuple[float, List[QualityFlag]]:
        """Returns (quality_score 0.0–1.0, list of flags)."""
        flags: List[QualityFlag] = []
        score = 1.0
        penalty = 0.0

        # Section completeness
        if not doc.content_sections:
            flags.append(QualityFlag(
                flag_id=f"QF-{doc.doc_id}-NO_SECTIONS",
                category="missing_data",
                description="Document has no content sections.",
                blocking=True,
            ))
            penalty += 0.40

        # Authority level
        if doc.authority in (AuthorityLevel.UNKNOWN, AuthorityLevel.ASSUMPTION):
            flags.append(QualityFlag(
                flag_id=f"QF-{doc.doc_id}-LOW_AUTHORITY",
                category="unverified_claim",
                description=f"Authority level is {doc.authority.value}.",
                blocking=False,
            ))
            penalty += 0.15

        # Traceability
        if not doc.traceability:
            flags.append(QualityFlag(
                flag_id=f"QF-{doc.doc_id}-NO_TRACEABILITY",
                category="missing_traceability",
                description="No traceability links defined.",
                blocking=False,
            ))
            penalty += 0.10

        # Freshness
        if doc.freshness in (DocumentFreshness.STALE, DocumentFreshness.REASSESSMENT_REQUIRED):
            flags.append(QualityFlag(
                flag_id=f"QF-{doc.doc_id}-STALE",
                category="stale_reference",
                description=f"Document freshness is {doc.freshness.value}.",
                blocking=False,
            ))
            penalty += 0.15

        # Conflicts
        if doc.conflicts:
            for conflict in doc.conflicts:
                flags.append(QualityFlag(
                    flag_id=f"QF-{doc.doc_id}-CONFLICT-{conflict.conflict_id}",
                    category="conflict",
                    description=f"Unresolved conflict: {conflict.description}",
                    blocking=True,
                ))
                penalty += 0.20

        # Approver check
        if doc.status in (DocumentStatus.APPROVED, DocumentStatus.PUBLISHED) and not doc.approver:
            flags.append(QualityFlag(
                flag_id=f"QF-{doc.doc_id}-NO_APPROVER",
                category="missing_approval",
                description="Approved/Published document has no approver recorded.",
                blocking=True,
            ))
            penalty += 0.20

        final_score = max(0.0, round(score - penalty, 3))
        return final_score, flags
