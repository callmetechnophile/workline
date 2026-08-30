"""
Amazon Bedrock reasoning provider for EngineeringExecutionAgent.
"""

import json
from loguru import logger
from research_agents.engineering_execution_agent.config import exec_config
from research_agents.engineering_execution_agent.providers.base import ReasoningProvider


class BedrockProvider(ReasoningProvider):
    """Amazon Bedrock integration using Claude 3.5 Sonnet."""

    def __init__(self):
        self.model_id = exec_config.model_id
        self.region = exec_config.aws_region
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("bedrock-runtime", region_name=self.region)
            except Exception as e:
                logger.warning(f"Failed to initialize boto3 bedrock-runtime client: {e}")
                self._client = None
        return self._client

    async def analyze_task(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Fallback deterministic execution active."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": exec_config.max_tokens,
                "temperature": exec_config.temperature,
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
            logger.error(f"Error invoking Bedrock model: {e}")
            return f"Error invoking Bedrock model: {e}"
