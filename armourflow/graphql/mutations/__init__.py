"""GraphQL mutations root package."""

import strawberry
from armourflow.graphql.mutations.task_mutations import TaskMutations
from armourflow.graphql.mutations.project_mutations import ProjectMutations
from armourflow.graphql.mutations.document_mutations import DocumentMutations


@strawberry.type
class Mutation(
    TaskMutations,
    ProjectMutations,
    DocumentMutations,
):
    """ArmourFlow Unified GraphQL Mutation Root."""
    pass
