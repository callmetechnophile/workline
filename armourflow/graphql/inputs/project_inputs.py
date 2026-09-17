"""
Project input types for GraphQL mutations.
"""

from typing import Optional
import strawberry


@strawberry.input
class CreateProjectInput:
    project_id: str
    title: str
    description: Optional[str] = None
