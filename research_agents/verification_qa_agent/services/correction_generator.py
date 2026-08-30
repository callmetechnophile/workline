"""
Correction report generator for VerificationQAAgent (Section 50).
Synthesizes prescriptive remediation requests for failed checks without modifying source code.
"""

from typing import List
import uuid
from research_agents.verification_qa_agent.schemas import (
    ChangeObject,
    ConformanceResult,
    CorrectionReportItem,
    RequirementVerificationItem,
    SecurityFinding,
    TaskVerificationObject,
    TestResultObject,
)


class CorrectionGenerator:
    """Synthesizes actionable remediation requests for QA failures."""

    def generate_corrections(
        self,
        changes: List[ChangeObject],
        tasks: List[TaskVerificationObject],
        requirements: List[RequirementVerificationItem],
        test_results: List[TestResultObject],
        security_findings: List[SecurityFinding],
        arch_conf: ConformanceResult,
        bom_conf: ConformanceResult,
    ) -> List[CorrectionReportItem]:
        corrections: List[CorrectionReportItem] = []

        # 1. Security corrections
        for sec in security_findings:
            corrections.append(
                CorrectionReportItem(
                    correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                    failure_id=sec.finding_id,
                    problem=f"{sec.category.upper()} Vulnerability: {sec.description}",
                    evidence=[f"{sec.file}:{sec.line or 1} - {sec.masked_snippet}"],
                    affected_tasks=[],
                    affected_files=[sec.file],
                    recommended_correction=f"Remove {sec.category} and use secure environment variable configuration.",
                    revalidation_required=True,
                )
            )

        # 2. Scope & File corrections
        for ch in changes:
            if ch.status == "FAIL":
                corrections.append(
                    CorrectionReportItem(
                        correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                        failure_id=f"FAIL-FILE-{uuid.uuid4().hex[:4].upper()}",
                        problem=f"Unauthorized/Unexpected File Change: {ch.file}",
                        evidence=[f"File: {ch.file}, Type: {ch.change_type}, Authorized: {ch.authorized}"],
                        affected_tasks=[ch.task_id] if ch.task_id else [],
                        affected_files=[ch.file],
                        recommended_correction="Revert unauthorized modification or update implementation authorization scope.",
                        revalidation_required=True,
                    )
                )

        # 3. Test failure corrections
        for tr in test_results:
            if tr.status in ("FAIL", "ERROR"):
                corrections.append(
                    CorrectionReportItem(
                        correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                        failure_id=tr.test_id,
                        problem=f"Test Suite Failure: {tr.command}",
                        evidence=[tr.output_reference or "Test failure observed."],
                        affected_tasks=[],
                        affected_files=[],
                        recommended_correction="Inspect test output and fix implementation defect.",
                        revalidation_required=True,
                    )
                )

        # 4. Conformance corrections
        if arch_conf.status == "FAIL":
            for v in arch_conf.violations:
                corrections.append(
                    CorrectionReportItem(
                        correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                        failure_id="FAIL-ARCH-001",
                        problem=f"Architecture Conformance Violation: {v}",
                        evidence=[arch_conf.details],
                        affected_tasks=[],
                        affected_files=[],
                        recommended_correction="Refactor implementation to strictly follow validated architecture flows.",
                        revalidation_required=True,
                    )
                )

        if bom_conf.status == "FAIL":
            for bv in bom_conf.violations:
                corrections.append(
                    CorrectionReportItem(
                        correction_id=f"CORR-{uuid.uuid4().hex[:6].upper()}",
                        failure_id="FAIL-BOM-001",
                        problem=f"BOM Conformance Violation: {bv}",
                        evidence=[bom_conf.details],
                        affected_tasks=[],
                        affected_files=[],
                        recommended_correction="Use only components explicitly approved in the engineering BOM.",
                        revalidation_required=True,
                    )
                )

        return corrections
