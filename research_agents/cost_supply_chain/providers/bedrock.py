"""
Amazon Bedrock reasoning provider for Agent #25 (Claude 3.5 Sonnet).
"""

import json
from typing import Optional
from loguru import logger
from research_agents.cost_supply_chain.config import config
from research_agents.cost_supply_chain.providers.base import BaseReasoningProvider


class BedrockReasoningProvider(BaseReasoningProvider):
    """Bedrock Converse / Invoke provider."""

    def __init__(self, model_id: Optional[str] = None, region: Optional[str] = None):
        self.model_id = model_id or config.model_id
        self.region = region or config.aws_region
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
            except Exception as e:
                logger.warning(f"Failed to initialize boto3 Bedrock client: {e}")
                self._client = None
        return self._client

    async def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
    ) -> str:
        client = self._get_client()
        if not client:
            return "Bedrock provider unavailable. Using deterministic heuristic fallback."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2048,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                body["system"] = system_prompt

            response = client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType="application/json",
                accept="application/json",
            )
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            return resp_body["content"][0]["text"]
        except Exception as e:
            logger.error(f"Bedrock invocation error: {e}")
            return f"Heuristic analysis fallback due to provider error: {str(e)}"
