"""
Amazon Bedrock reasoning provider for VerificationQAAgent (Section 65).
Used for complex failure interpretation and ambiguous relationship reasoning without overruling deterministic results.
"""

import json
from loguru import logger
from research_agents.verification_qa_agent.config import qa_config
from research_agents.verification_qa_agent.providers.base import ReasoningProvider


class BedrockQAProvider(ReasoningProvider):
    """Amazon Bedrock integration using Claude 3.5 Sonnet for QA interpretation."""

    def __init__(self):
        self.model_id = qa_config.model_id
        self.region = qa_config.aws_region
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

    async def analyze_qa(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Fallback deterministic QA verification active."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": qa_config.max_tokens,
                "temperature": qa_config.temperature,
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
            logger.error(f"Error invoking Bedrock model for QA: {e}")
            return f"Error invoking Bedrock model: {e}"
