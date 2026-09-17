"""
Security Dashboard Aggregator and Security Gate Evaluator (Agent #22).
"""

from typing import List
from research_agents.security_threat.schemas import (
    AttackSurfaceEntry,
    SecurityControl,
    SecurityDashboardData,
    SecurityFinding,
    SecurityGateLiteral,
    ThreatMitigation,
    ThreatObject,
)


class DashboardService:
    """Aggregates security posture and determines security gate status."""

    def aggregate(
        self,
        project_id: str,
        threats: List[ThreatObject],
        attack_surface: List[AttackSurfaceEntry],
        controls: List[SecurityControl],
        mitigations: List[ThreatMitigation],
        findings: List[SecurityFinding],
    ) -> SecurityDashboardData:
        total = len(threats)
        crit_t = sum(1 for t in threats if t.is_critical or (t.severity and t.severity >= 5))
        high_t = sum(1 for t in threats if t.severity == 4 and not t.is_critical)
        med_t = sum(1 for t in threats if t.severity == 3)
        low_t = sum(1 for t in threats if t.severity and t.severity < 3)

        open_f = sum(1 for f in findings if f.status == "OPEN")
        ver_ctrl = sum(1 for c in controls if c.verification_status == "VERIFIED")
        unver_ctrl = sum(1 for c in controls if c.verification_status != "VERIFIED")

        pub_surf = sum(1 for e in attack_surface if e.exposure == "PUBLIC")
        priv_surf = sum(1 for e in attack_surface if "A2A" in e.type or "CLI" in e.type)

        cross_tenant = sum(1 for t in threats if t.category == "TENANT_ISOLATION")
        credential_r = sum(1 for t in threats if t.category in ("CREDENTIAL_THEFT", "SECRETS_EXPOSURE"))
        pi_r = sum(1 for t in threats if t.category == "PROMPT_INJECTION")
        a2a_r = sum(1 for t in threats if t.category == "A2A_ATTACK")
        supply_r = sum(1 for t in threats if t.category == "SUPPLY_CHAIN")

        # Deterministic security score calculation (starts at 100, penalties for open critical/high threats)
        score = max(0.0, 100.0 - (crit_t * 15.0 + high_t * 5.0 + open_f * 2.0))

        gate: SecurityGateLiteral = "SECURITY_PASS"
        if crit_t > 0:
            gate = "SECURITY_BLOCKED"
        elif high_t > 0 or unver_ctrl > 2:
            gate = "SECURITY_REVIEW_REQUIRED"

        return SecurityDashboardData(
            project_id=project_id,
            total_threats=total,
            critical_threats=crit_t,
            high_threats=high_t,
            medium_threats=med_t,
            low_threats=low_t,
            open_findings=open_f,
            verified_controls=ver_ctrl,
            unverified_controls=unver_ctrl,
            public_attack_surfaces=pub_surf,
            privileged_attack_surfaces=priv_surf,
            cross_tenant_risks=cross_tenant,
            credential_risks=credential_r,
            prompt_injection_risks=pi_r,
            a2a_risks=a2a_r,
            supply_chain_risks=supply_r,
            security_score=round(score, 1),
            security_gate=gate,
        )
