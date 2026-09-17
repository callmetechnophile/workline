"""
Task input types for GraphQL mutations.
"""

from typing import Optional
import strawberry
from strawberry.scalars import JSON


@strawberry.input
class CreateTaskInput:
    agent_id: Optional[str] = None
    capability: Optional[str] = None
    project_id: str = "default"
    payload: JSON = strawberry.field(default_factory=dict)


@strawberry.input
class RunCapabilityTaskInput:
    capability: str
    project_id: str = "default"
    payload: JSON = strawberry.field(default_factory=dict)
