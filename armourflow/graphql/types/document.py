"""
Technical documentation GraphQL types.
"""

from typing import List, Optional
import strawberry
from strawberry.scalars import JSON


@strawberry.type
class QualityFlagType:
    code: str
    severity: str
    message: str


@strawberry.type
class TechnicalDocumentType:
    doc_id: str
    project_id: str
    document_type: str
    title: str
    status: str
    author: str
    authority: str
    content: str
    quality_flags: List[QualityFlagType]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
