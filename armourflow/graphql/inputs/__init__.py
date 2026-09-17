"""GraphQL inputs package."""

from armourflow.graphql.inputs.task_inputs import CreateTaskInput, RunCapabilityTaskInput
from armourflow.graphql.inputs.project_inputs import CreateProjectInput
from armourflow.graphql.inputs.document_inputs import CreateDocumentInput

__all__ = [
    "CreateTaskInput",
    "RunCapabilityTaskInput",
    "CreateProjectInput",
    "CreateDocumentInput",
]
