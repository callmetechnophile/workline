"""
Workline AI — Amazon Bedrock Anthropic Claude Adapter.

Formats requests and parses responses for Claude models (Haiku, Sonnet) on Amazon Bedrock.
Conforms to the Bedrock Anthropic Messages API specification.
"""

from typing import Any, Dict, List, Optional
from backend.workline.ai.bedrock.client import BedrockClient, bedrock_client
from backend.workline.ai.bedrock.schemas import AIResponse, ChatMessage, TokenUsage


class AnthropicBedrockAdapter:
    """Adapter for Claude 3.5 Haiku and Claude 3.5 / 3.7 Sonnet on Amazon Bedrock."""

    def __init__(self, client: Optional[BedrockClient] = None):
        self.client = client or bedrock_client

    def generate(
        self,
        model_id: str,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.2,
        top_p: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
    ) -> AIResponse:
        """
        Executes a prompt against a Claude model on Bedrock and returns a normalized AIResponse.
        """
        # Format messages for Anthropic Bedrock API
        formatted_messages = [
            {"role": m.role if m.role in ("user", "assistant") else "user", "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        # Extract system prompt if present in messages
        system_content = system_instruction
        if not system_content:
            sys_msgs = [m.content for m in messages if m.role == "system"]
            if sys_msgs:
                system_content = "\n\n".join(sys_msgs)

        body: Dict[str, Any] = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": formatted_messages,
            "temperature": temperature,
        }

        if system_content:
            body["system"] = system_content
        if top_p is not None:
            body["top_p"] = top_p
        if stop_sequences:
            body["stop_sequences"] = stop_sequences

        res = self.client.invoke_model(model_id=model_id, body=body)
        raw_data = res.get("data", {})
        latency_ms = res.get("latency_ms", 0.0)
        request_id = res.get("request_id", "")

        # Extract text content
        content_blocks = raw_data.get("content", [])
        text_pieces = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
        full_text = "".join(text_pieces)

        # Extract usage metrics
        usage_data = raw_data.get("usage", {})
        in_tokens = usage_data.get("input_tokens", 0)
        out_tokens = usage_data.get("output_tokens", 0)

        return AIResponse(
            text=full_text,
            model_id=model_id,
            provider="Anthropic (via Amazon Bedrock)",
            request_id=request_id or raw_data.get("id"),
            usage=TokenUsage(
                prompt_tokens=in_tokens,
                completion_tokens=out_tokens,
                total_tokens=in_tokens + out_tokens,
            ),
            latency_ms=latency_ms,
            finish_reason=raw_data.get("stop_reason", "stop"),
            raw_response=raw_data,
        )


anthropic_adapter = AnthropicBedrockAdapter()
