"""
Configuration settings for EngineeringKnowledgeGraphAgent (Agent #13).
"""

import os
from pydantic import BaseModel, Field


class GraphConfig(BaseModel):
    """Configuration for Agent #13 SurrealDB Knowledge Graph & Project State Agent."""

    # SurrealDB connection settings
    surrealdb_url: str = Field(
        default_factory=lambda: os.getenv(
            "SURREALDB_URL", os.getenv("WORKLINE_SURREALDB_URL", "http://127.0.0.1:8001")
        )
    )
    surrealdb_namespace: str = Field(
        default_factory=lambda: os.getenv(
            "SURREALDB_NAMESPACE", os.getenv("WORKLINE_SURREALDB_NAMESPACE", "main")
        )
    )
    surrealdb_database: str = Field(
        default_factory=lambda: os.getenv(
            "SURREALDB_DATABASE", os.getenv("WORKLINE_SURREALDB_DATABASE", "main")
        )
    )
    surrealdb_user: str = Field(
        default_factory=lambda: os.getenv(
            "SURREALDB_USER", os.getenv("WORKLINE_SURREALDB_USER", "root")
        )
    )
    surrealdb_password: str = Field(
        default_factory=lambda: os.getenv(
            "SURREALDB_PASSWORD", os.getenv("WORKLINE_SURREALDB_PASSWORD", "root")
        )
    )

    # Bedrock reasoning settings
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_GRAPH_MODEL_ID", "us.anthropic.claude-3-5-sonnet-20241022-v2:0"
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("GRAPH_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("GRAPH_MAX_TOKENS", "4096"))
    )

    # Graph Traversal Limits (Section 107)
    max_traversal_depth: int = Field(
        default_factory=lambda: int(os.getenv("GRAPH_MAX_DEPTH", "15"))
    )
    max_nodes_per_query: int = Field(
        default_factory=lambda: int(os.getenv("GRAPH_MAX_NODES", "5000"))
    )
    query_timeout_sec: int = Field(
        default_factory=lambda: int(os.getenv("GRAPH_QUERY_TIMEOUT_SEC", "30"))
    )


graph_config = GraphConfig()
