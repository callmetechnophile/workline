"""
Unified Strawberry GraphQL Schema for ArmourFlow AI.
"""

import strawberry
from strawberry.schema.config import StrawberryConfig
from armourflow.graphql.queries import Query
from armourflow.graphql.mutations import Mutation
from armourflow.graphql.subscriptions import Subscription
from armourflow.graphql.security import QueryDepthAndComplexityLimiter

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription,
    extensions=[
        QueryDepthAndComplexityLimiter,
    ],
    config=StrawberryConfig(auto_camel_case=True),
)
