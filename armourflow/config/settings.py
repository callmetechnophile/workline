"""Typed platform settings loading from environment and .env."""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# pyrefly: ignore [missing-import]
from armourflow.config.environment import EnvironmentMode, get_environment

# Load .env safely from root
load_dotenv()


class PlatformSettings(BaseModel):
    """Authoritative platform configuration schema."""

    # Application
    app_env: EnvironmentMode = Field(default_factory=get_environment)
    app_name: str = Field(default_factory=lambda: os.getenv("APP_NAME", "ArmourFlow AI"))
    app_version: str = Field(default_factory=lambda: os.getenv("APP_VERSION", "1.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "10000")))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    # CLI
    cli_output_format: str = Field(default_factory=lambda: os.getenv("CLI_OUTPUT_FORMAT", "rich"))
    cli_default_project: str = Field(default_factory=lambda: os.getenv("CLI_DEFAULT_PROJECT", "default"))

    # Google ADK Runtime
    adk_enabled: bool = Field(
        default_factory=lambda: os.getenv("ADK_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    adk_runtime: str = Field(default_factory=lambda: os.getenv("ADK_RUNTIME", "google_adk_v1"))

    # Control Fabric
    control_fabric_endpoint: str = Field(
        default_factory=lambda: os.getenv("CONTROL_FABRIC_ENDPOINT", "internal://control-fabric")
    )
    control_fabric_timeout: float = Field(
        default_factory=lambda: float(os.getenv("CONTROL_FABRIC_TIMEOUT", "60.0"))
    )

    # SurrealDB
    surrealdb_url: str = Field(
        default_factory=lambda: os.getenv("SURREALDB_URL", "ws://localhost:8000/rpc")
    )
    surrealdb_namespace: str = Field(
        default_factory=lambda: os.getenv("SURREALDB_NAMESPACE", "workline")
    )
    surrealdb_database: str = Field(
        default_factory=lambda: os.getenv("SURREALDB_DATABASE", "workline")
    )
    surrealdb_user: str = Field(
        default_factory=lambda: os.getenv("SURREALDB_USER", "root")
    )
    surrealdb_password: str = Field(
        default_factory=lambda: os.getenv("SURREALDB_PASSWORD", "root")
    )

    # Amazon Bedrock
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION") or os.getenv("AWS_REGION") or "us-east-1"
    )
    bedrock_region: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    )
    bedrock_model_id: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_REASONING_MODEL_ID") or os.getenv("BEDROCK_MODEL_ID") or "anthropic.claude-3-5-sonnet-20241022-v2:0"
    )
    bedrock_fast_model_id: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_FAST_CODE_MODEL_ID") or "anthropic.claude-3-5-haiku-20241022-v1:0"
    )
    bedrock_embedding_model_id: str = Field(
        default_factory=lambda: os.getenv("BEDROCK_EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v2:0")
    )

    # Interoperability: A2A
    a2a_enabled: bool = Field(
        default_factory=lambda: os.getenv("A2A_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    a2a_endpoint: str = Field(
        default_factory=lambda: os.getenv("A2A_ENDPOINT", "internal://a2a-gateway")
    )

    # Interoperability: Bindu
    bindu_enabled: bool = Field(
        default_factory=lambda: os.getenv("BINDU_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    bindu_endpoint: str = Field(
        default_factory=lambda: os.getenv("BINDU_ENDPOINT", "http://localhost:8080/bindu")
    )
    bindu_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("BINDU_API_KEY")
    )

    # External Tools: Tavily
    tavily_enabled: bool = Field(
        default_factory=lambda: os.getenv("TAVILY_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    tavily_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY")
    )

    # External Tools: arXiv (Academic Literature)
    arxiv_enabled: bool = Field(
        default_factory=lambda: os.getenv("ARXIV_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    arxiv_endpoint: str = Field(
        default_factory=lambda: os.getenv("ARXIV_BASE_URL", "https://export.arxiv.org/api/query")
    )

    # External Tools: FreePHDLabor (Legacy)
    freephdlabor_enabled: bool = Field(
        default_factory=lambda: os.getenv("FREEPHDLABOR_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    freephdlabor_endpoint: str = Field(
        default_factory=lambda: os.getenv("FREEPHDLABOR_BASE_URL") or os.getenv("FREEPHDLABOR_ENDPOINT") or "https://api.freephdlabor.com/v1"
    )
    freephdlabor_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("FREEPHDLABOR_API_KEY")
    )

    # External Tools: Anakin (Self-hosted or anakin.io scraper)
    anakin_enabled: bool = Field(
        default_factory=lambda: os.getenv("ANAKIN_ENABLED", "false").lower() in ("true", "1", "yes")
    )
    anakin_endpoint: str = Field(
        default_factory=lambda: os.getenv("ANAKIN_BASE_URL") or os.getenv("ANAKIN_ENDPOINT") or "https://api.anakin.io/v1"
    )
    anakin_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ANAKIN_API_KEY")
    )

    # ArmorIQ Authorization Boundary
    armoriq_enabled: bool = Field(
        default_factory=lambda: os.getenv("ARMORIQ_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    armoriq_endpoint: str = Field(
        default_factory=lambda: os.getenv("ARMOURIQ_BASE_URL") or os.getenv("ARMORIQ_ENDPOINT") or "https://api.armouriq.io"
    )
    armoriq_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("ARMOURIQ_API_KEY") or os.getenv("ARMORIQ_SECRET_KEY")
    )

    # Evaluation Harness
    harness_enabled: bool = Field(
        default_factory=lambda: os.getenv("HARNESS_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    harness_endpoint: str = Field(
        default_factory=lambda: os.getenv("HARNESS_ENDPOINT", "internal://harness")
    )

    # 14. GraphQL Client/Application API Layer
    graphql_enabled: bool = Field(
        default_factory=lambda: os.getenv("GRAPHQL_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    graphql_path: str = Field(
        default_factory=lambda: os.getenv("GRAPHQL_PATH", "/graphql")
    )
    graphql_playground_enabled: bool = Field(
        default_factory=lambda: os.getenv("GRAPHQL_PLAYGROUND_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    graphql_introspection_enabled: bool = Field(
        default_factory=lambda: os.getenv("GRAPHQL_INTROSPECTION_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    graphql_max_query_depth: int = Field(
        default_factory=lambda: int(os.getenv("GRAPHQL_MAX_QUERY_DEPTH", "10"))
    )
    graphql_max_query_complexity: int = Field(
        default_factory=lambda: int(os.getenv("GRAPHQL_MAX_QUERY_COMPLEXITY", "100"))
    )
    graphql_request_timeout: float = Field(
        default_factory=lambda: float(os.getenv("GRAPHQL_REQUEST_TIMEOUT", "30.0"))
    )


@lru_cache()
def get_settings() -> PlatformSettings:
    """Singleton getter for platform settings."""
    return PlatformSettings()
