"""
GraphQL request context and dependency injection.
"""

import uuid
from typing import Optional
from fastapi import Request
from strawberry.fastapi import BaseContext
from armourflow.config import get_settings, PlatformSettings
from armourflow.fabric import get_control_fabric, AgentControlFabric
from armourflow.data import get_database_client, PlatformDatabaseClient
from armourflow.security import get_security_boundary, ArmorIQBoundary


class GraphQLContext(BaseContext):
    """Per-request context containing authenticated user and central client handles."""

    def __init__(
        self,
        request: Optional[Request] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        auth_token: Optional[str] = None,
    ):
        super().__init__()
        self.request = request
        self.request_id = f"gql_{uuid.uuid4().hex[:12]}"
        self.user_id = user_id or "anonymous"
        self.project_id = project_id or "default"
        self.auth_token = auth_token

        # Injected central singletons
        self.settings: PlatformSettings = get_settings()
        self.fabric: AgentControlFabric = get_control_fabric()
        self.db: PlatformDatabaseClient = get_database_client()
        self.security: ArmorIQBoundary = get_security_boundary()


async def get_graphql_context(request: Request) -> GraphQLContext:
    """FastAPI dependency to build GraphQLContext from HTTP headers."""
    user_id = request.headers.get("x-user-id", "anonymous")
    project_id = request.headers.get("x-project-id", "default")
    auth_token = request.headers.get("authorization")
    return GraphQLContext(
        request=request,
        user_id=user_id,
        project_id=project_id,
        auth_token=auth_token,
    )
