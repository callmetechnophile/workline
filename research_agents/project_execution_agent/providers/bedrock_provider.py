"""
Amazon Bedrock reasoning provider for ProjectExecutionAgent (Agent #10).
"""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.project_execution_agent.config import planning_config
from research_agents.project_execution_agent.providers.base import ReasoningProvider
from research_agents.project_execution_agent.schemas import WorkPackage


class BedrockExecutionProvider(ReasoningProvider):
    """Amazon Bedrock Claude 3.5 Sonnet implementation planning provider."""

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or planning_config.bedrock_model_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("bedrock-runtime")
        return self._client

    async def generate_work_breakdown(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        validation: Dict[str, Any],
    ) -> List[WorkPackage]:
        prompt = f"""You are the ProjectExecutionAgent (Agent #10) in WorkflowGuide AI.
Given the verified system architecture, BOM components, and validation rules below, generate a comprehensive Work Breakdown Structure (WBS) with discrete atomic execution tasks.

Project: {json.dumps(project_context)}
Architecture: {json.dumps(architecture)}
BOM: {json.dumps(bom)}
Validation: {json.dumps(validation)}

Return a strict JSON array of WorkPackage objects.
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": planning_config.max_tokens,
                "temperature": planning_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                raw_packages = json.loads(content[start:end])
                return [WorkPackage.model_validate(p) for p in raw_packages]
        except Exception as e:
            logger.warning(f"BedrockExecutionProvider fallback to deterministic generator: {e}")
        
        from research_agents.project_execution_agent.providers.mock_provider import MockProjectExecutionProvider
        mock = MockProjectExecutionProvider()
        return await mock.generate_work_breakdown(project_context, architecture, bom, validation)
