"""
Amazon Bedrock reasoning provider for EngineeringKnowledgeGraphAgent (Section 79).
Used for semantic graph query explanations without altering graph state or executing arbitrary SQL.
"""

import json
from loguru import logger
from research_agents.engineering_knowledge_graph_agent.config import graph_config
from research_agents.engineering_knowledge_graph_agent.providers.base import ReasoningProvider


class BedrockGraphProvider(ReasoningProvider):
    """Amazon Bedrock integration using Claude 3.5 Sonnet for semantic graph summaries."""

    def __init__(self):
        self.model_id = graph_config.model_id
        self.region = graph_config.aws_region
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

    async def explain_graph(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Fallback deterministic graph explanation active."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": graph_config.max_tokens,
                "temperature": graph_config.temperature,
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
            logger.error(f"Error invoking Bedrock model for Graph explanation: {e}")
            return f"Error invoking Bedrock model: {e}"
