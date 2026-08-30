import json
from loguru import logger
from research_agents.engineering_optimization.config import optimization_config
from research_agents.engineering_optimization.providers.base import ReasoningProvider


class BedrockOptimizationProvider(ReasoningProvider):
    def __init__(self):
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import boto3
                self._client = boto3.client("bedrock-runtime", region_name=optimization_config.aws_region)
            except Exception as e:
                logger.warning(f"Bedrock client init failed: {e}")
        return self._client

    async def explain_tradeoff(self, prompt: str, system_prompt: str = "") -> str:
        client = self._get_client()
        if client is None:
            return "[Bedrock unavailable] Trade-off reasoning skipped."
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": optimization_config.max_tokens,
                "temperature": optimization_config.temperature,
                "system": system_prompt or "You are an expert engineering optimization advisor.",
                "messages": [{"role": "user", "content": prompt}],
            })
            response = client.invoke_model(modelId=optimization_config.model_id, body=body,
                                           contentType="application/json", accept="application/json")
            result = json.loads(response["body"].read())
            return result["content"][0]["text"]
        except Exception as e:
            logger.warning(f"Bedrock explain_tradeoff error: {e}")
            return f"[Bedrock error: {e}]"
