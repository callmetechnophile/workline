"""
Deterministic Mock reasoning provider for SecurityThreatModelingAgent (Agent #22).
"""

from typing import Any, Dict, List
from research_agents.security_threat.providers.base import ReasoningProvider
from research_agents.security_threat.schemas import (
    AssetObject,
    AttackPath,
    AttackSurfaceEntry,
    ThreatMitigation,
    ThreatObject,
)


class MockSecurityProvider(ReasoningProvider):
    """Deterministic mock reasoning provider for testing and offline threat modeling."""

    async def analyze_threat_scenarios(
        self,
        project_context: Dict[str, Any],
        assets: List[AssetObject],
        attack_surface: List[AttackSurfaceEntry],
    ) -> List[ThreatObject]:
        project_id = project_context.get("project_id", "PROJECT-001")

        # Threat 1: Prompt Injection / Instruction Hierarchy Hijacking
        t1 = ThreatObject(
            threat_id="THREAT-PI-001",
            project_id=project_id,
            title="Indirect Prompt Injection via Untrusted Engineering Documents",
            description="Adversary embeds malicious system instructions inside uploaded PDF/DOCX or web research pages to hijack agent tool execution.",
            category="PROMPT_INJECTION",
            asset_ids=["ASSET-AGENT-RUN", "ASSET-BOM-DATA"],
            entry_point_ids=["ENTRY-FILE-UPLOAD", "ENTRY-WEB-SEARCH"],
            actor_ids=["ACTOR-EXTERNAL-WEB"],
            attack_path_ids=["PATH-INDIRECT-PI"],
            severity=4,
            likelihood=4,
            risk_score=16,
            status="IDENTIFIED",
            is_critical=False,
        )

        # Threat 2: Cross-Tenant Isolation Bypass in SurrealDB Queries
        t2 = ThreatObject(
            threat_id="THREAT-TENANT-001",
            project_id=project_id,
            title="Cross-Tenant / Cross-Project Data Exfiltration via Graph Traversal",
            description="Attacker attempts to query graph relationships across project boundaries without validating project_id scoping.",
            category="TENANT_ISOLATION",
            asset_ids=["ASSET-GRAPH-DB", "ASSET-PROJECT-SECRETS"],
            entry_point_ids=["ENTRY-PUBLIC-API", "ENTRY-A2A-MSG"],
            actor_ids=["ACTOR-MALICIOUS-TENANT"],
            attack_path_ids=["PATH-GRAPH-TRAVERSAL"],
            severity=5,
            likelihood=2,
            risk_score=10,
            status="IDENTIFIED",
            is_critical=False,
        )

        # Threat 3: A2A Message Spoofing and Unauthorized Tool Invocation
        t3 = ThreatObject(
            threat_id="THREAT-A2A-001",
            project_id=project_id,
            title="Agent Impersonation and Privileged Tool Execution Bypass",
            description="Compromised worker agent sends fabricated A2A authorization tokens to EngineeringExecutionAgent (Agent #11) to execute arbitrary shell commands.",
            category="A2A_ATTACK",
            asset_ids=["ASSET-ARMORIQ-TOKEN", "ASSET-EXEC-SHELL"],
            entry_point_ids=["ENTRY-A2A-FABRIC"],
            actor_ids=["ACTOR-COMPROMISED-AGENT"],
            attack_path_ids=["PATH-A2A-SPOOF"],
            severity=5,
            likelihood=2,
            risk_score=10,
            status="IDENTIFIED",
            is_critical=False,
        )

        # Threat 4: Secrets Exposure in Debug Logs and A2A Payloads
        t4 = ThreatObject(
            threat_id="THREAT-SECRET-001",
            project_id=project_id,
            title="API Key and Credential Leakage in Telemetry & Logs",
            description="Third-party API keys (Bedrock/Tavily/Anakin) inadvertently included in unstructured exception traces or event messages.",
            category="SECRETS_EXPOSURE",
            asset_ids=["ASSET-API-KEYS", "ASSET-LOGS"],
            entry_point_ids=["ENTRY-OBSERVABILITY"],
            actor_ids=["ACTOR-INSIDER-AUDITOR"],
            attack_path_ids=["PATH-LOG-HARVEST"],
            severity=5,
            likelihood=2,
            risk_score=10,
            status="IDENTIFIED",
            is_critical=False,
        )

        return [t1, t2, t3, t4]

    async def suggest_security_mitigations(
        self,
        threat: ThreatObject,
        attack_path: AttackPath,
    ) -> List[ThreatMitigation]:
        if threat.category == "PROMPT_INJECTION":
            return [
                ThreatMitigation(
                    mitigation_id="MIT-SEC-001",
                    threat_id=threat.threat_id,
                    action="Enforce strict content boundary delimiters and isolate untrusted document text in non-executable data frames",
                    priority="HIGH",
                    owner="Agent Security Team",
                    status="PROPOSED",
                ),
                ThreatMitigation(
                    mitigation_id="MIT-SEC-002",
                    threat_id=threat.threat_id,
                    action="Require secondary ArmorIQ user confirmation before executing write/delete tools originating from web search context",
                    priority="HIGH",
                    owner="ArmorIQ Policy Team",
                    status="PROPOSED",
                ),
            ]
        elif threat.category == "TENANT_ISOLATION":
            return [
                ThreatMitigation(
                    mitigation_id="MIT-SEC-003",
                    threat_id=threat.threat_id,
                    action="Enforce parameterized SurrealDB queries with mandatory WHERE project_id = $project_id and team_id = $team_id constraints",
                    priority="CRITICAL",
                    owner="Database Architecture Team",
                    status="PROPOSED",
                )
            ]
        elif threat.category == "A2A_ATTACK":
            return [
                ThreatMitigation(
                    mitigation_id="MIT-SEC-004",
                    threat_id=threat.threat_id,
                    action="Cryptographically sign all A2A messages with ephemeral session tokens validated against AgentRegistry before tool dispatch",
                    priority="CRITICAL",
                    owner="Control Fabric Team",
                    status="PROPOSED",
                )
            ]
        else:
            return [
                ThreatMitigation(
                    mitigation_id="MIT-SEC-005",
                    threat_id=threat.threat_id,
                    action="Implement automated regex secret scrubbing middleware on all Loguru structured logging handlers and A2A payload formatters",
                    priority="HIGH",
                    owner="Infrastructure Security Team",
                    status="PROPOSED",
                )
            ]
