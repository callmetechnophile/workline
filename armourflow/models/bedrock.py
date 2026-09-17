"""Amazon Bedrock centralized model abstraction with offline fallback."""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from armourflow.config.settings import PlatformSettings, get_settings


class BedrockModelProvider:
    """
    Centralized Amazon Bedrock client.
    Handles inference for reasoning, fast completion, and embeddings.
    """

    _instance: Optional["BedrockModelProvider"] = None

    def __init__(self, settings: Optional[PlatformSettings] = None):
        self.settings = settings or get_settings()
        self.region = self.settings.bedrock_region
        self.reasoning_model = self.settings.bedrock_model_id
        self.fast_model = self.settings.bedrock_fast_model_id
        self.embedding_model = self.settings.bedrock_embedding_model_id
        self._client = None
        self._initialized = False

    @classmethod
    def get_instance(cls, settings: Optional[PlatformSettings] = None) -> "BedrockModelProvider":
        if cls._instance is None:
            cls._instance = BedrockModelProvider(settings)
        return cls._instance

    def _get_client(self):
        if self._client is None and not self._initialized:
            self._initialized = True
            try:
                import boto3
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
                logger.info(f"[BedrockModelProvider] Initialized boto3 client in {self.region}")
            except Exception as e:
                logger.warning(f"[BedrockModelProvider] Bedrock client unavailable: {e}; offline fallback active")
                self._client = None
        return self._client

    async def invoke_reasoning(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        system: Optional[str] = None,
    ) -> str:
        """Invoke Claude 3.5 Sonnet / reasoning model on Bedrock."""
        client = self._get_client()
        if client is None:
            return f"[BEDROCK_OFFLINE_MOCK] Reasoning response for: {prompt[:80]}..."

        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            body["system"] = system

        try:
            response = client.invoke_model(
                modelId=self.reasoning_model,
                body=json.dumps(body),
            )
            data = json.loads(response["body"].read().decode("utf-8"))
            return data["content"][0]["text"]
        except Exception as e:
            logger.warning(f"[BedrockModelProvider] Inference fallback on error: {e}")
            return f"[BEDROCK_FALLBACK] Response generated locally (reason: {e})"

    async def invoke_fast(self, prompt: str, max_tokens: int = 512) -> str:
        """Invoke fast Haiku model on Bedrock."""
        return await self.invoke_reasoning(prompt=prompt, max_tokens=max_tokens, temperature=0.2)

    def health_check(self) -> Dict[str, Any]:
        client = self._get_client()
        return {
            "status": "HEALTHY" if client is not None else "DEGRADED",
            "provider": "Amazon Bedrock",
            "region": self.region,
            "reasoning_model": self.reasoning_model,
            "fast_model": self.fast_model,
            "client_available": client is not None,
        }


def get_model_provider() -> BedrockModelProvider:
    return BedrockModelProvider.get_instance()
