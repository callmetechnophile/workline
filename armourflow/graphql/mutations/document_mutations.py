"""
Technical document creation and review GraphQL mutations.
Routes strictly through the Control Fabric -> Agent #27 (TechDocAgent).
"""

import strawberry
from strawberry.types import Info
from armourflow.graphql.inputs.document_inputs import CreateDocumentInput
from armourflow.graphql.types.document import TechnicalDocumentType, QualityFlagType
from armourflow.graphql.errors import create_graphql_error, GraphQLErrorCode


@strawberry.type
class DocumentMutations:
    @strawberry.mutation
    async def create_technical_document(self, info: Info, input: CreateDocumentInput) -> TechnicalDocumentType:
        """Submit a document drafting command via the Control Fabric to Agent #27."""
        ctx = info.context
        task = await ctx.fabric.submit_task(
            payload={
                "project_id": input.project_id,
                "operation": "create_document",
                "user_id": ctx.user_id,
                "document_type": input.document_type,
                "title": input.title,
                "content": input.content,
                "authority_claim": input.authority_claim,
            },
            target_agent_id="agent.27",
            project_id=input.project_id,
            user_id=ctx.user_id,
        )

        if task.error or not task.result:
            raise create_graphql_error(
                task.error or "Failed creating technical document.",
                code=GraphQLErrorCode.TASK_REJECTED,
                details={"task_id": task.task_id},
            )

        doc = task.result.get("document", {})
        q_flags = [
            QualityFlagType(
                code=q.get("code", "QUAL"),
                severity=q.get("severity", "INFO"),
                message=q.get("message", ""),
            )
            for q in task.result.get("quality_flags", [])
        ]

        return TechnicalDocumentType(
            doc_id=doc.get("doc_id", "DOC-UNKNOWN"),
            project_id=doc.get("project_id", input.project_id),
            document_type=doc.get("document_type", input.document_type),
            title=doc.get("title", input.title),
            status=doc.get("status", "DRAFT"),
            author=doc.get("author", ctx.user_id),
            authority=doc.get("authority", "UNKNOWN"),
            content=doc.get("content", input.content),
            quality_flags=q_flags,
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
        )
