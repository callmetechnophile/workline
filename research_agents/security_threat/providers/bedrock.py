"""
Amazon Bedrock reasoning provider for SecurityThreatModelingAgent (Agent #22).
"""

import json
from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.security_threat.config import security_config
from research_agents.security_threat.providers.base import ReasoningProvider
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    ThreatMitigation,
    ThreatObject,
)


class BedrockSecurityProvider(ReasoningProvider):
    """Amazon Bedrock Claude 3.5 Sonnet security threat analysis provider."""

    def __init__(self, model_id: Optional[str] = None):
        self.model_id = model_id or security_config.bedrock_model_id
        self._client = None

    def _get_client(self):
        if self._client is None:
            import boto3
            self._client = boto3.client("bedrock-runtime")
        return self._client

    async def analyze_threat_scenarios(
        self,
        project_context: Dict[str, Any],
        assets: List[AssetObject],
        attack_surface: List[AttackSurfaceEntry],
    ) -> List[ThreatObject]:
        prompt = f"""You are the SecurityThreatModelingAgent (Agent #22) in WorkflowGuide AI.
Analyze the following system assets and exposed attack surfaces to identify plausible security threats (STRIDE + Agentic AI threats like prompt injection, tool poisoning, A2A tampering, secrets exposure).
DO NOT fabricate CVE IDs, CVSS vectors, or unverifiable claims.

Project: {json.dumps(project_context)}
Assets: {[a.model_dump() for a in assets]}
Attack Surface: {[e.model_dump() for e in attack_surface]}

Return a strict JSON list of ThreatObject items.
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": security_config.max_tokens,
                "temperature": security_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                raw = json.loads(content[start:end])
                return [ThreatObject.model_validate(item) for item in raw]
        except Exception as e:
            logger.warning(f"BedrockSecurityProvider analyze_threat_scenarios fallback: {e}")

        from research_agents.security_threat.providers.mock_provider import MockSecurityProvider
        mock = MockSecurityProvider()
        return await mock.analyze_threat_scenarios(project_context, assets, attack_surface)

    async def suggest_security_mitigations(
        self,
        threat: ThreatObject,
        attack_path: AttackPath,
    ) -> List[ThreatMitigation]:
        prompt = f"""Suggest technical cybersecurity mitigations for:
Threat: {threat.title} ({threat.category})
Attack Path: {' -> '.join(attack_path.steps)}
Target Asset: {attack_path.target_asset}

Return a strict JSON list of ThreatMitigation items.
"""
        try:
            client = self._get_client()
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": security_config.max_tokens,
                "temperature": security_config.temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            response = client.invoke_model(modelId=self.model_id, body=json.dumps(body))
            resp_body = json.loads(response["body"].read().decode("utf-8"))
            content = resp_body["content"][0]["text"]
            start = content.find("[")
            end = content.rfind("]") + 1
            if start != -1 and end > start:
                raw = json.loads(content[start:end])
                return [ThreatMitigation.model_validate(item) for item in raw]
        except Exception as e:
            logger.warning(f"BedrockSecurityProvider suggest_security_mitigations fallback: {e}")

        from research_agents.security_threat.providers.mock_provider import MockSecurityProvider
        mock = MockSecurityProvider()
        return await mock.suggest_security_mitigations(threat, attack_path)
