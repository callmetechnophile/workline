"""
Standardized GraphQL error handling with domain error extensions.
"""

from typing import Any, Dict, Optional
from strawberry.exceptions import StrawberryGraphQLError


class GraphQLErrorCode:
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    TASK_REJECTED = "TASK_REJECTED"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    AGENT_UNAVAILABLE = "AGENT_UNAVAILABLE"
    CONTROL_FABRIC_ERROR = "CONTROL_FABRIC_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    TIMEOUT = "TIMEOUT"
    RATE_LIMITED = "RATE_LIMITED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


def create_graphql_error(
    message: str,
    code: str,
    details: Optional[Dict[str, Any]] = None,
) -> StrawberryGraphQLError:
    """Create a structured Strawberry GraphQL error with code extension."""
    extensions = {"code": code}
    if details:
        extensions["details"] = details
    return StrawberryGraphQLError(message, extensions=extensions)
