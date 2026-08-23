"""
Workline AI — Amazon Bedrock Normalized Data Schemas.

Defines standardized, provider-agnostic request and response objects for all AI inference.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Normalized token consumption metrics."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatMessage(BaseModel):
    """Standardized conversation message."""
    role: str = "user"  # 'system', 'user', 'assistant'
    content: str


class AIResponse(BaseModel):
    """
    Standardized AI response returned across all Bedrock models (Claude, DeepSeek, Nova, Titan).
    Shields Workline from provider-specific JSON response structures.
    """
    text: str
    model_id: str
    provider: str
    request_id: Optional[str] = None
    usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0
    finish_reason: Optional[str] = "stop"
    tool_calls: Optional[List[Dict[str, Any]]] = None
    structured_output: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


class BedrockImageRequest(BaseModel):
    """Standardized image generation request for Bedrock image models."""
    prompt: str
    negative_prompt: Optional[str] = None
    aspect_ratio: str = "16:9"
    width: int = 1280
    height: int = 720
    seed: Optional[int] = None
    cfg_scale: float = 7.0
    number_of_images: int = 1


class BedrockImageResponse(BaseModel):
    """Standardized image response from Bedrock image generation models."""
    image_bytes: bytes
    mime_type: str = "image/png"
    model_id: str
    width: int = 1280
    height: int = 720
    seed: Optional[int] = None
    finish_reason: str = "SUCCESS"
