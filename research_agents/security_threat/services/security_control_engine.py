"""
Security Control Mapping, Mitigation Tracking, and Least-Privilege Assessor (Agent #22).
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from research_agents.security_threat.schemas import (
    SecurityControl,
    ThreatMitigation,
    ThreatObject,
)


class SecurityControlEngine:
    """Maps existing security controls and evaluates least-privilege compliance."""

    def get_standard_controls(self) -> List[SecurityControl]:
        return [
            SecurityControl(
                control_id="CTRL-ARMORIQ-SCOPE",
                name="ArmorIQ Least-Privilege Scope Map Enforcement",
                category="AUTHORIZATION",
                description="Strict static and delegation token scope validation preventing unauthorized tool invocation.",
                implemented=True,
                implementation_reference="backend/armoriq/scope_map.py",
                verification_status="VERIFIED",
            ),
            SecurityControl(
                control_id="CTRL-JWT-AUTH",
                name="HMAC-SHA256 JWT Session Authentication",
                category="AUTHENTICATION",
                description="Stateless cryptographically verified session tokens with 1-hour expiration.",
                implemented=True,
                implementation_reference="backend/auth/",
                verification_status="VERIFIED",
            ),
            SecurityControl(
                control_id="CTRL-PYDANTIC-VALIDATION",
                name="Pydantic Strict Schema & Input Validation",
                category="INPUT_VALIDATION",
                description="Guarantees type-safety and field validation on all API requests and A2A messages.",
                implemented=True,
                implementation_reference="research_agents/*/schemas.py",
                verification_status="VERIFIED",
            ),
            SecurityControl(
                control_id="CTRL-SECRETS-ENV",
                name="OS Environment Variable Secrets Isolation",
                category="SECRETS_MANAGEMENT",
                description="Credentials ingested exclusively via environment variables, never hardcoded in source.",
                implemented=True,
                implementation_reference=".env / OS Env",
                verification_status="VERIFIED",
            ),
            SecurityControl(
                control_id="CTRL-PROMPT-GUARD",
                name="Document & Web Content Isolation Framing",
                category="PROMPT_GUARD",
                description="Delimits untrusted external data in XML tags, blocking direct instruction execution.",
                implemented=True,
                implementation_reference="research_agents/security_threat/services/security_control_engine.py",
                verification_status="UNVERIFIED",
            ),
        ]

    def verify_control(
        self,
        control: SecurityControl,
        evidence: Dict[str, Any],
    ) -> SecurityControl:
        verdict = evidence.get("status") or evidence.get("verdict")
        if verdict in ("PASS", "VERIFIED"):
            control.verification_status = "VERIFIED"
            if evidence.get("evidence_id"):
                control.evidence_ids.append(evidence["evidence_id"])
            logger.info(f"SecurityControl {control.control_id} marked VERIFIED by Agent #18.")
        else:
            logger.warning(f"SecurityControl {control.control_id} verification evidence invalid: {verdict}")
        return control

    def assess_least_privilege(
        self,
        agents_topology: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Flag agents requesting capabilities beyond declared role requirements."""
        excessive = []
        for ag in (agents_topology or []):
            name = ag.get("name", "")
            caps = ag.get("capabilities", [])
            # Read-only research agents requesting shell / filesystem write
            if "research" in name.lower() and any("write" in c or "shell" in c for c in caps):
                excessive.append(f"{name}: Research agent holds privileged write/shell execution capabilities")
        return excessive
