"""
Amazon Bedrock provider for Technical Documentation Agent.
LLM generates prose only; deterministic code controls all metadata.
"""
import json
from typing import Dict

from research_agents.documentation_agent.providers.base import BaseDocProvider


class BedrockDocProvider(BaseDocProvider):

    def __init__(self, model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"):
        self._model_id = model_id
        try:
            import boto3
            self._client = boto3.client("bedrock-runtime", region_name="us-east-1")
        except Exception:
            self._client = None

    def _invoke(self, prompt: str) -> str:
        if self._client is None:
            return "[BEDROCK UNAVAILABLE — OFFLINE MODE]"
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "temperature": 0.1,
            "messages": [{"role": "user", "content": prompt}],
        })
        response = self._client.invoke_model(modelId=self._model_id, body=body)
        payload  = json.loads(response["body"].read())
        return payload["content"][0]["text"]

    def generate_section(self, section_name: str, context: Dict) -> str:
        prompt = (
            f"You are a technical writer for an engineering project.\n"
            f"Generate the '{section_name}' section of a {context.get('document_type', '')} "
            f"document titled '{context.get('title', '')}'.\n"
            f"Context: {json.dumps(context, indent=2)}\n"
            f"Write clear, precise prose. Do NOT invent measurements, test results, "
            f"approvals, or compliance claims. Use DATA_REQUIRED where data is missing."
        )
        return self._invoke(prompt)

    def summarize_changes(self, old_text: str, new_text: str) -> str:
        prompt = (
            f"Summarize the key changes between these two document versions in one paragraph.\n"
            f"OLD:\n{old_text[:800]}\n\nNEW:\n{new_text[:800]}"
        )
        return self._invoke(prompt)
