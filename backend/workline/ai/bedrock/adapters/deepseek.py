"""
Workline AI — Amazon Bedrock DeepSeek Adapter.

Formats requests and parses responses for DeepSeek models (R1, V3) on Amazon Bedrock.
Normalizes DeepSeek reasoning outputs into standardized AIResponse objects.
"""

from typing import Any, Dict, List, Optional
from backend.workline.ai.bedrock.client import BedrockClient, bedrock_client
from backend.workline.ai.bedrock.schemas import AIResponse, ChatMessage, TokenUsage


class DeepSeekBedrockAdapter:
    """Adapter for DeepSeek R1 and DeepSeek V3 on Amazon Bedrock."""

    def __init__(self, client: Optional[BedrockClient] = None):
        self.client = client or bedrock_client

    def generate(
        self,
        model_id: str,
        messages: List[ChatMessage],
        system_instruction: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.6,
        top_p: float = 0.95,
    ) -> AIResponse:
        """
        Executes a prompt against a DeepSeek model on Bedrock and returns a normalized AIResponse.
        """
        formatted_messages = []
        if system_instruction:
            formatted_messages.append({"role": "system", "content": system_instruction})

        for m in messages:
            formatted_messages.append({"role": m.role, "content": m.content})

        # DeepSeek Bedrock inference payload
        body: Dict[str, Any] = {
            "messages": formatted_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

        res = self.client.invoke_model(model_id=model_id, body=body)
        raw_data = res.get("data", {})
        latency_ms = res.get("latency_ms", 0.0)
        request_id = res.get("request_id", "")

        # Extract text from choices or direct outputs
        generated_text = ""
        finish_reason = "stop"

        if "choices" in raw_data and len(raw_data["choices"]) > 0:
            choice = raw_data["choices"][0]
            if "message" in choice:
                generated_text = choice["message"].get("content", "")
            elif "text" in choice:
                generated_text = choice.get("text", "")
            finish_reason = choice.get("finish_reason", "stop")
        elif "generation" in raw_data:
            generated_text = raw_data.get("generation", "")
        elif "output" in raw_data:
            generated_text = raw_data.get("output", "")

        # Extract token metrics
        usage_data = raw_data.get("usage", {})
        prompt_tokens = usage_data.get("prompt_tokens", 0)
        comp_tokens = usage_data.get("completion_tokens", 0)
        total_tokens = usage_data.get("total_tokens", prompt_tokens + comp_tokens)

        return AIResponse(
            text=generated_text,
            model_id=model_id,
            provider="DeepSeek (via Amazon Bedrock)",
            request_id=request_id or raw_data.get("id"),
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                total_tokens=total_tokens,
            ),
            latency_ms=latency_ms,
            finish_reason=finish_reason,
            raw_response=raw_data,
        )


deepseek_adapter = DeepSeekBedrockAdapter()
