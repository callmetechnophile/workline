"""
Pydantic data models and schemas for LLM Gateway.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMCapability(str, Enum):
    """Functional capability types handled by AI/LLM providers."""
    TEXT_GENERATION = "TEXT_GENERATION"
    CHAT_COMPLETION = "CHAT_COMPLETION"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    IMAGE_EDITING = "IMAGE_EDITING"
    EMBEDDINGS = "EMBEDDINGS"


class LLMRequest(BaseModel):
    """Normalized multi-model LLM request."""
    prompt: str
    system_instruction: Optional[str] = None
    model_alias: str = "fast"  # 'fast', 'reasoning', 'default'
    capability: LLMCapability = Field(default=LLMCapability.TEXT_GENERATION)
    temperature: float = 0.2
    max_tokens: int = 2048
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LLMUsage(BaseModel):
    """Token and cost telemetry."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


class LLMResponse(BaseModel):
    """Standardized LLM completion response."""
    text: str
    model_id: str
    provider: str
    usage: LLMUsage = Field(default_factory=LLMUsage)
    latency_ms: float = 0.0
