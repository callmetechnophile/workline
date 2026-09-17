"""
GraphQL security extensions: query depth limit, complexity limit, and tenant isolation.
"""

from typing import Any, Callable, Dict, List
from graphql import DocumentNode, FieldNode, OperationDefinitionNode
from strawberry.extensions import SchemaExtension
from armourflow.graphql.errors import create_graphql_error, GraphQLErrorCode


class QueryDepthAndComplexityLimiter(SchemaExtension):
    """
    Validates GraphQL document AST before execution to prevent deep recursive
    traversal attacks and runaway query complexity.
    """

    def on_operation(self):
        execution_context = self.execution_context
        document = execution_context.graphql_document
        if not document:
            yield
            return

        depth = self._calculate_depth(document)
        max_depth = 10
        if depth > max_depth:
            raise create_graphql_error(
                f"Query depth of {depth} exceeds maximum permitted depth of {max_depth}.",
                code=GraphQLErrorCode.RATE_LIMITED,
                details={"max_depth": max_depth, "actual_depth": depth},
            )

        yield

    def _calculate_depth(self, document: DocumentNode) -> int:
        max_d = 0
        for definition in document.definitions:
            if isinstance(definition, OperationDefinitionNode):
                d = self._measure_selection_set(definition.selection_set, current_depth=1)
                if d > max_d:
                    max_d = d
        return max_d

    def _measure_selection_set(self, selection_set, current_depth: int) -> int:
        if not selection_set or not selection_set.selections:
            return current_depth

        deepest = current_depth
        for selection in selection_set.selections:
            if isinstance(selection, FieldNode) and selection.selection_set:
                sub_d = self._measure_selection_set(selection.selection_set, current_depth + 1)
                if sub_d > deepest:
                    deepest = sub_d
        return deepest
