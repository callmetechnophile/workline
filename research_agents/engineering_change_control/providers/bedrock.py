"""
Amazon Bedrock reasoning provider for EngineeringChangeControlAgent (Section 59).
"""

import json
from loguru import logger
from research_agents.engineering_change_control.config import change_control_config
from research_agents.engineering_change_control.providers.base import ReasoningProvider


class BedrockChangeControlProvider(ReasoningProvider):
    """Bedrock Claude 3.5 Sonnet provider for change justification and risk analysis."""

    def __init__(self):
        self.model_id = change_control_config.model_id
        self.region = change_control_config.aws_region
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
            except Exception as e:
                logger.warning(f"Failed to initialize boto3 bedrock client: {e}")
                self._client = None
        return self._client

    async def explain_change(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Operating in deterministic change analysis mode."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": change_control_config.max_tokens,
                "temperature": change_control_config.temperature,
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
            logger.error(f"Error invoking Bedrock for ChangeControl: {e}")
            return f"Error invoking Bedrock: {e}"
