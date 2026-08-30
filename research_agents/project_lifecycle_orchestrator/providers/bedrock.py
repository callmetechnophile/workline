"""
Amazon Bedrock reasoning provider for ProjectLifecycleOrchestrator (Section 48).
Used for natural language explanations and failure classification without altering graph state or granting authorizations.
"""

import json
from loguru import logger
from research_agents.project_lifecycle_orchestrator.config import orchestrator_config
from research_agents.project_lifecycle_orchestrator.providers.base import ReasoningProvider


class BedrockOrchestratorProvider(ReasoningProvider):
    """Bedrock Claude 3.5 Sonnet provider for failure classification and explanation."""

    def __init__(self):
        self.model_id = orchestrator_config.model_id
        self.region = orchestrator_config.aws_region
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

    async def reason(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Operating in deterministic rule mode."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": orchestrator_config.max_tokens,
                "temperature": orchestrator_config.temperature,
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
            logger.error(f"Error invoking Bedrock for orchestration: {e}")
            return f"Error invoking Bedrock: {e}"
