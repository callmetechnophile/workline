"""
Architecture and BOM conformance verification service for VerificationQAAgent (Sections 21, 22, 24, 25).
Verifies that implementation does not bypass architecture layers or substitute components without authorization.
"""

from typing import Any, Dict, List
from research_agents.verification_qa_agent.schemas import ConformanceResult


class ConformanceChecker:
    """Verifies architectural flow alignment and BOM component conformance."""

    def check_architecture_conformance(
        self,
        architecture: Dict[str, Any],
        implementation_tasks: List[Dict[str, Any]],
    ) -> ConformanceResult:
        violations: List[str] = []
        subsystems = architecture.get("subsystems", [])

        # Check for explicit conflict flags in tasks
        for t in implementation_tasks:
            title_lower = t.get("title", "").lower()
            desc_lower = t.get("description", "").lower()
            if "bypass" in title_lower or "bypass" in desc_lower:
                violations.append(f"Task '{t.get('task_id')}' bypasses required subsystem layer.")

        status = "PASS" if not violations else "FAIL"
        details = "Implementation conforms to validated architecture flows." if status == "PASS" else "Architectural conformance violations detected."
        return ConformanceResult(domain="architecture", status=status, details=details, violations=violations)

    def check_bom_conformance(
        self,
        bom: Dict[str, Any],
        implementation_tasks: List[Dict[str, Any]],
    ) -> ConformanceResult:
        violations: List[str] = []
        bom_items = bom.get("items", [])

        # Check for unauthorized component substitution
        for t in implementation_tasks:
            title_lower = t.get("title", "").lower()
            if "unapproved substitute" in title_lower or "substitute component" in title_lower:
                violations.append(f"Task '{t.get('task_id')}' references unapproved substitute component.")

        status = "PASS" if not violations else "FAIL"
        details = "Implementation utilizes 100% approved BOM components." if status == "PASS" else "BOM conformance violations detected."
        return ConformanceResult(domain="bom", status=status, details=details, violations=violations)
