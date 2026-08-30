"""
Compliance gate service evaluating overall project readiness (Sections 40–42).
Determines ALLOW, BLOCK, REVIEW_REQUIRED, INSUFFICIENT_EVIDENCE, and ALLOW_WITH_APPROVED_EXCEPTION.
"""

from datetime import datetime, timezone
from typing import List
from research_agents.engineering_compliance.schemas import (
    ComplianceGateLiteral,
    ComplianceResult,
    ComplianceStatusLiteral,
    ComplianceWaiver,
    ProjectComplianceSummary,
)


class ComplianceGateService:
    """Evaluates compliance gate verdict based on deterministic rule outcomes."""

    def evaluate_gate(
        self,
        project_id: str,
        results: List[ComplianceResult],
        waivers: List[ComplianceWaiver],
    ) -> ProjectComplianceSummary:
        total = len(results)
        passed = sum(1 for r in results if r.status == "PASS")
        failed = sum(1 for r in results if r.status == "FAIL")
        warnings = sum(1 for r in results if r.status == "WARNING")
        reviews = sum(1 for r in results if r.status == "REVIEW")
        unknowns = sum(1 for r in results if r.status == "UNKNOWN")
        crit_fails = sum(1 for r in results if r.status == "FAIL" and r.severity == "CRITICAL")
        high_fails = sum(1 for r in results if r.status == "FAIL" and r.severity == "HIGH")

        # Active non-expired waivers
        active_waivers = [
            w for w in waivers
            if w.status == "APPROVED" and datetime.fromisoformat(w.expires_at) > datetime.now(timezone.utc)
        ]
        waived_rules = {w.rule_id for w in active_waivers}

        # Gate Evaluation
        gate: ComplianceGateLiteral = "ALLOW"
        overall_status: ComplianceStatusLiteral = "PASS"
        blocking = False

        if crit_fails > 0:
            # Check if all critical failures are waived
            unwaived_crit = [r for r in results if r.status == "FAIL" and r.severity == "CRITICAL" and r.rule_id not in waived_rules]
            if unwaived_crit:
                gate = "BLOCK"
                overall_status = "FAIL"
                blocking = True
            else:
                gate = "ALLOW_WITH_APPROVED_EXCEPTION"
                overall_status = "FAIL"

        elif reviews > 0:
            gate = "REVIEW_REQUIRED"
            overall_status = "REVIEW"

        elif unknowns > 0:
            gate = "INSUFFICIENT_EVIDENCE"
            overall_status = "UNKNOWN"

        elif failed > 0:
            unwaived_fail = [r for r in results if r.status == "FAIL" and r.rule_id not in waived_rules]
            if unwaived_fail:
                gate = "BLOCK"
                overall_status = "FAIL"
                blocking = True
            else:
                gate = "ALLOW_WITH_APPROVED_EXCEPTION"
                overall_status = "FAIL"

        return ProjectComplianceSummary(
            project_id=project_id,
            status=overall_status,
            gate=gate,
            total_checks=total,
            passed=passed,
            failed=failed,
            warnings=warnings,
            review_required=reviews,
            unknown=unknowns,
            critical_failures=crit_fails,
            high_failures=high_fails,
            blocking=blocking,
        )
