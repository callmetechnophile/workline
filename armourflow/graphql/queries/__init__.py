"""GraphQL queries root package."""

import strawberry
from armourflow.graphql.queries.system_queries import SystemQueries
from armourflow.graphql.queries.agent_queries import AgentQueries
from armourflow.graphql.queries.task_queries import TaskQueries
from armourflow.graphql.queries.project_queries import ProjectQueries
from armourflow.graphql.queries.evaluation_queries import EvaluationQueries


@strawberry.type
class Query(
    SystemQueries,
    AgentQueries,
    TaskQueries,
    ProjectQueries,
    EvaluationQueries,
):
    """ArmourFlow Unified GraphQL Query Root."""
    pass
