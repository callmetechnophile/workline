"""
Document input types for GraphQL mutations.
"""

from typing import Optional
import strawberry


@strawberry.input
class CreateDocumentInput:
    project_id: str
    title: str
    document_type: str = "TECHNICAL_REPORT"
    content: str = ""
    authority_claim: str = "UNKNOWN"
