"""
Amazon Bedrock reasoning provider for EngineeringSimulationAgent (Section 69).
"""

import json
from loguru import logger
from research_agents.engineering_simulation.config import simulation_config
from research_agents.engineering_simulation.providers.base import ReasoningProvider


class BedrockSimulationProvider(ReasoningProvider):
    """Bedrock Claude 3.5 Sonnet provider for simulation report explanation."""

    def __init__(self):
        self.model_id = simulation_config.model_id
        self.region = simulation_config.aws_region
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

    async def explain_simulation(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if not client:
            return "Bedrock client not available. Operating in deterministic numerical simulation mode."

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": simulation_config.max_tokens,
                "temperature": simulation_config.temperature,
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
            logger.error(f"Error invoking Bedrock for Simulation: {e}")
            return f"Error invoking Bedrock: {e}"
