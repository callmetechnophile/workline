"""
FastAPI GraphQL Router for Strawberry GraphQL.
"""

from typing import Optional
from fastapi import Request, WebSocket
from strawberry.fastapi import GraphQLRouter
from armourflow.config import get_settings
from armourflow.graphql.schema import schema
from armourflow.graphql.context import GraphQLContext, get_graphql_context


async def get_context(request: Request) -> GraphQLContext:
    return await get_graphql_context(request)


def get_graphql_router() -> GraphQLRouter:
    """Factory creating configured GraphQLRouter for FastAPI application."""
    settings = get_settings()
    graphql_ide = "graphiql" if settings.graphql_playground_enabled else None
    return GraphQLRouter(
        schema=schema,
        context_getter=get_context,
        path=settings.graphql_path,
        graphql_ide=graphql_ide,
        allow_queries_via_get=True,
    )
