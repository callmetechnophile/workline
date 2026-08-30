"""
Configuration settings for VerificationQAAgent (Agent #12).
"""

import os
from pydantic import BaseModel, Field


class QAConfig(BaseModel):
    """Configuration for Agent #12 QA Agent."""

    # Bedrock reasoning configuration
    model_id: str = Field(
        default_factory=lambda: os.getenv(
            "BEDROCK_QA_MODEL_ID",
            "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        )
    )
    aws_region: str = Field(
        default_factory=lambda: os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    )
    temperature: float = Field(
        default_factory=lambda: float(os.getenv("QA_TEMPERATURE", "0.0"))
    )
    max_tokens: int = Field(
        default_factory=lambda: int(os.getenv("QA_MAX_TOKENS", "4096"))
    )

    # Verification settings
    pytest_timeout_sec: int = Field(
        default_factory=lambda: int(os.getenv("QA_PYTEST_TIMEOUT_SEC", "120"))
    )
    strict_security: bool = Field(
        default_factory=lambda: os.getenv("QA_STRICT_SECURITY", "true").lower() == "true"
    )
    max_scan_file_size_kb: int = Field(
        default_factory=lambda: int(os.getenv("QA_MAX_SCAN_FILE_SIZE_KB", "1024"))
    )


qa_config = QAConfig()
