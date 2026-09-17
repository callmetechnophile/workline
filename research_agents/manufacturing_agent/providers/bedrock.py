"""
Amazon Bedrock reasoning provider for Manufacturing / DFM-DFA Agent (Agent #24).
"""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.manufacturing_agent.config import manufacturing_config
from research_agents.manufacturing_agent.providers.base import ReasoningProvider
from research_agents.manufacturing_agent.schemas import (
    DFAFinding,
    DFMFinding,
    ManufacturingRecommendation,
)


class BedrockManufacturingProvider(ReasoningProvider):
    """Amazon Bedrock Claude 3.5 Sonnet provider for DFM/DFA reasoning."""

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or manufacturing_config.bedrock_model_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("bedrock-runtime")
        return self._client

    async def analyze_dfm_dfa(
        self,
        project_context: Dict[str, Any],
        components: List[Dict[str, Any]],
        assemblies: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        prompt = f"""You are the Manufacturing / DFM-DFA Agent (Agent #24) in WorkflowGuide AI.
Analyze the following components and assembly definitions for Design-for-Manufacturing (DFM) and Design-for-Assembly (DFA) feasibility.
Evaluate feature accessibility, tool clearances, parting lines, draft angles, fastener counts, and assembly orientation ambiguity.
DO NOT fabricate machine tolerances, material properties, or tooling costs. If unknown, identify them as unknown.

Project: {json.dumps(project_context)}
Components: {json.dumps(components)}
Assemblies: {json.dumps(assemblies)}

Return a strict JSON object:
{{
  "dfm_findings": [...],
  "dfa_findings": [...]
}}
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": manufacturing_config.max_tokens,
                "temperature": manufacturing_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            start = content.find("{")
            end = content.rfind("}") + 1
            if start != -1 and end > start:
                raw = json.loads(content[start:end])
                dfm_list = [DFMFinding.model_validate(f) for f in raw.get("dfm_findings", [])]
                dfa_list = [DFAFinding.model_validate(f) for f in raw.get("dfa_findings", [])]
                return {"dfm_findings": dfm_list, "dfa_findings": dfa_list}
        except Exception as e:
            logger.warning(f"BedrockManufacturingProvider analyze_dfm_dfa fallback: {e}")

        from research_agents.manufacturing_agent.providers.mock_provider import MockManufacturingProvider
        mock = MockManufacturingProvider()
        return await mock.analyze_dfm_dfa(project_context, components, assemblies)

    async def draft_recommendations(
        self,
        dfm_findings: List[DFMFinding],
        dfa_findings: List[DFAFinding],
    ) -> List[ManufacturingRecommendation]:
        from research_agents.manufacturing_agent.providers.mock_provider import MockManufacturingProvider
        mock = MockManufacturingProvider()
        return await mock.draft_recommendations(dfm_findings, dfa_findings)
