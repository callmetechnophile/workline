"""
Amazon Bedrock reasoning provider for EngineeringRiskAgent (Agent #21).
"""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.engineering_risk.config import risk_config
from research_agents.engineering_risk.providers.base import ReasoningProvider
from research_agents.engineering_risk.schemas import FailureMode, RiskMitigation, RiskObject


class BedrockRiskProvider(ReasoningProvider):
    """Amazon Bedrock Claude 3.5 Sonnet risk and failure mode extraction provider."""

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or risk_config.bedrock_model_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("bedrock-runtime")
        return self._client

    async def extract_failure_modes(
        self,
        project_context: Dict[str, Any],
        architecture: Dict[str, Any],
        bom: Dict[str, Any],
        interfaces: List[Dict[str, Any]],
    ) -> List[FailureMode]:
        prompt = f"""You are the EngineeringRiskAgent (Agent #21) in WorkflowGuide AI.
Analyze the following engineering system and extract potential failure modes, causes, effects, and controls.
DO NOT invent arbitrary failure rates or probabilities. If data is unknown, state UNKNOWN.

Project: {json.dumps(project_context)}
Architecture: {json.dumps(architecture)}
BOM: {json.dumps(bom)}
Interfaces: {json.dumps(interfaces)}

Return a strict JSON list of FailureMode objects.
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": risk_config.max_tokens,
                "temperature": risk_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                raw = json.loads(content[start:end])
                return [FailureMode.model_validate(item) for item in raw]
        except Exception as e:
            logger.warning(f"BedrockRiskProvider extract_failure_modes fallback: {e}")

        from research_agents.engineering_risk.providers.mock_provider import MockRiskProvider
        mock = MockRiskProvider()
        return await mock.extract_failure_modes(project_context, architecture, bom, interfaces)

    async def suggest_mitigations(
        self,
        risk: RiskObject,
        failure_mode: FailureMode,
    ) -> List[RiskMitigation]:
        prompt = f"""Suggest technical engineering mitigations for this failure mode:
Risk: {risk.title} ({risk.category})
Failure Mode: {failure_mode.description}
Causes: {[c.description for c in failure_mode.causes]}
Effects: {failure_mode.local_effect} -> {failure_mode.system_effect}

Return a strict JSON list of RiskMitigation objects.
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": risk_config.max_tokens,
                "temperature": risk_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                raw = json.loads(content[start:end])
                return [RiskMitigation.model_validate(item) for item in raw]
        except Exception as e:
            logger.warning(f"BedrockRiskProvider suggest_mitigations fallback: {e}")

        from research_agents.engineering_risk.providers.mock_provider import MockRiskProvider
        mock = MockRiskProvider()
        return await mock.suggest_mitigations(risk, failure_mode)
