"""
STRIDE and Agentic AI Threat Modeling & Attack Path Engine (Agent #22).
"""

from typing import List, Optional
from research_agents.security_threat.config import security_config
from research_agents.security_threat.schemas import (
    AttackPath,
    AttackSurfaceEntry,
    ThreatActor,
    ThreatObject,
)


class ThreatModelingEngine:
    """Deterministic STRIDE + Agentic AI threat evaluator and multi-step attack path builder."""

    def calculate_risk_score(
        self,
        likelihood: Optional[int],
        impact: Optional[int],
    ) -> int:
        """Deterministic calculation of Security Risk Score (Score = L * I)."""
        l = max(1, min(5, likelihood or 3))
        i = max(1, min(5, impact or 3))
        return l * i

    def is_critical_threat(self, threat: ThreatObject) -> bool:
        """Determine if threat triggers critical security override."""
        score = threat.risk_score or (self.calculate_risk_score(threat.likelihood, threat.severity))
        # High impact (5) or score >= critical threshold
        if (threat.severity and threat.severity >= 5) or score >= security_config.critical_risk_threshold:
            return True
        if threat.category in ("TENANT_ISOLATION", "AUTHORIZATION_BYPASS", "REMOTE_EXECUTION", "CREDENTIAL_THEFT"):
            if threat.severity and threat.severity >= 4:
                return True
        return False

    def build_attack_paths(
        self,
        threats: List[ThreatObject],
        attack_surface: List[AttackSurfaceEntry],
    ) -> List[AttackPath]:
        paths = []
        for t in threats:
            if t.category == "PROMPT_INJECTION":
                paths.append(
                    AttackPath(
                        attack_path_id=f"PATH-{t.threat_id}",
                        threat_id=t.threat_id,
                        steps=[
                            "Adversary uploads crafted PDF containing indirect prompt injection instructions",
                            "DocumentProcessingAgent (Agent #3) parses raw text without sanitization",
                            "EngineeringSynthesisAgent (Agent #5) consumes poisoned context into system prompt",
                            "Agent executes unauthorized tool calls under compromised instruction context",
                        ],
                        entry_point="ENTRY-FILE-UPLOAD",
                        target_asset="ASSET-AGENT-RUN",
                        required_privileges=["Unauthenticated / Public Document Submitter"],
                        controls_crossed=["TB-PUBLIC-API", "TB-API-FABRIC"],
                        likelihood=4,
                        impact=4,
                    )
                )
            elif t.category == "TENANT_ISOLATION":
                paths.append(
                    AttackPath(
                        attack_path_id=f"PATH-{t.threat_id}",
                        threat_id=t.threat_id,
                        steps=[
                            "Authenticated User in Team A constructs malicious graph query payload",
                            "EngineeringKnowledgeGraphAgent (Agent #13) executes unparameterized SurrealQL",
                            "Query traverses node relationships across Project B boundaries",
                            "Confidential engineering BOM and credentials of Team B returned to Team A",
                        ],
                        entry_point="ENTRY-PUBLIC-API",
                        target_asset="ASSET-GRAPH-DB",
                        required_privileges=["Authenticated User (Team A)"],
                        controls_crossed=["TB-API-FABRIC"],
                        likelihood=2,
                        impact=5,
                    )
                )
            elif t.category == "A2A_ATTACK":
                paths.append(
                    AttackPath(
                        attack_path_id=f"PATH-{t.threat_id}",
                        threat_id=t.threat_id,
                        steps=[
                            "Compromised or rogue agent process injects synthetic A2A message",
                            "Message claims origin from ProjectLifecycleOrchestrator (Agent #14)",
                            "EngineeringExecutionAgent (Agent #11) accepts task without verifying ArmorIQ delegation signature",
                            "Privileged shell tool executed on host filesystem",
                        ],
                        entry_point="ENTRY-A2A-FABRIC",
                        target_asset="ASSET-EXEC-SHELL",
                        required_privileges=["Local Process Subprocess Access"],
                        controls_crossed=["TB-FABRIC-EXEC"],
                        likelihood=2,
                        impact=5,
                    )
                )
            else:
                paths.append(
                    AttackPath(
                        attack_path_id=f"PATH-{t.threat_id}",
                        threat_id=t.threat_id,
                        steps=[
                            "External service returns unexpected exception or auth token in payload",
                            "Logging handler captures raw payload into observability logs",
                            "Unauthorized insider or log viewer harvests plain-text API credentials",
                        ],
                        entry_point="ENTRY-OBSERVABILITY",
                        target_asset="ASSET-API-KEYS",
                        required_privileges=["Log Viewer Role"],
                        controls_crossed=["TB-AGENT-EXTERNAL"],
                        likelihood=2,
                        impact=4,
                    )
                )
        return paths
