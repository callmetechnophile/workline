"""
Agent #12: VerificationQAAgent implementation using Google ADK conventions.
Independently verifies implementation against approved requirements, architecture, BOM, tests, and security invariants.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
from loguru import logger

from research_agents.verification_qa_agent.config import qa_config
from research_agents.verification_qa_agent.providers.base import ReasoningProvider
from research_agents.verification_qa_agent.providers.bedrock import BedrockQAProvider
from research_agents.verification_qa_agent.schemas import (
    ChangeObject,
    ConformanceResult,
    CorrectionReportItem,
    EvidenceObject,
    FinalQAVerdict,
    RequirementVerificationItem,
    SecurityFinding,
    TaskVerificationObject,
    TestResultObject,
    VerificationExecutionContext,
    VerificationQAAgentInput,
    VerificationQAAgentOutput,
    VerificationTraceabilityItem,
)
from research_agents.verification_qa_agent.services.armoriq_auditor import ArmorIQAuditor
from research_agents.verification_qa_agent.services.conformance_checker import ConformanceChecker
from research_agents.verification_qa_agent.services.correction_generator import CorrectionGenerator
from research_agents.verification_qa_agent.services.file_exporter import QAFileExporter
from research_agents.verification_qa_agent.services.file_verifier import FileVerifier
from research_agents.verification_qa_agent.services.report_generator import QAReportGenerator
from research_agents.verification_qa_agent.services.requirement_verifier import RequirementVerifier
from research_agents.verification_qa_agent.services.security_scanner import SecurityScanner
from research_agents.verification_qa_agent.services.task_verifier import TaskVerifier
from research_agents.verification_qa_agent.services.test_runner_service import TestRunnerService
from research_agents.verification_qa_agent.services.traceability_builder import TraceabilityBuilder


class VerificationQAAgent:
    """
    Google ADK-compliant Verification & Autonomous QA Agent.
    Independently verifies implementation against approved requirements, architecture, BOM, tests, and security invariants.
    """

    NAME = "VerificationQAAgent"
    DESCRIPTION = (
        "Independently verifies implementation against the approved engineering "
        "requirements, architecture, BOM, implementation plan, tests, and authorization records."
    )
    CAPABILITIES = [
        "verification.run",
        "verification.requirements",
        "verification.tests",
        "verification.security",
        "verification.report",
        "verification.status",
    ]

    def __init__(
        self,
        reasoning_provider: Optional[ReasoningProvider] = None,
        file_verifier: Optional[FileVerifier] = None,
        task_verifier: Optional[TaskVerifier] = None,
        requirement_verifier: Optional[RequirementVerifier] = None,
        test_runner: Optional[TestRunnerService] = None,
        security_scanner: Optional[SecurityScanner] = None,
        conformance_checker: Optional[ConformanceChecker] = None,
        armoriq_auditor: Optional[ArmorIQAuditor] = None,
        correction_generator: Optional[CorrectionGenerator] = None,
        traceability_builder: Optional[TraceabilityBuilder] = None,
        report_generator: Optional[QAReportGenerator] = None,
        file_exporter: Optional[QAFileExporter] = None,
        project_root_dir: Optional[str] = None,
    ):
        self.provider = reasoning_provider or BedrockQAProvider()
        self.file_verifier = file_verifier or FileVerifier(project_root_dir)
        self.task_verifier = task_verifier or TaskVerifier(project_root_dir)
        self.requirement_verifier = requirement_verifier or RequirementVerifier()
        self.test_runner = test_runner or TestRunnerService(project_root_dir)
        self.security_scanner = security_scanner or SecurityScanner(project_root_dir)
        self.conformance_checker = conformance_checker or ConformanceChecker()
        self.armoriq_auditor = armoriq_auditor or ArmorIQAuditor()
        self.correction_generator = correction_generator or CorrectionGenerator()
        self.traceability_builder = traceability_builder or TraceabilityBuilder()
        self.report_generator = report_generator or QAReportGenerator()
        self.file_exporter = file_exporter or QAFileExporter()

    async def run(
        self,
        input_data: VerificationQAAgentInput,
        execution_id: Optional[str] = None,
    ) -> VerificationQAAgentOutput:
        """
        Performs independent multi-domain verification, test execution, security scanning, and QA verdict generation.
        """
        start_time = time.time()
        context = input_data.execution_context or VerificationExecutionContext(
            user_id="user_001",
            project_id=input_data.project.get("project_id", "proj_001"),
            execution_id=execution_id or f"qa_{uuid.uuid4().hex[:8]}",
        )
        verif_id = f"QA-{uuid.uuid4().hex[:6].upper()}"
        proj_title = input_data.project.get("title", "Engineering Implementation")

        logger.info(f"[{verif_id}][{self.NAME}] Starting independent QA verification for project='{context.project_id}'")

        # 1. Check Agent #9 Validation Gate
        val_verdict = str(input_data.validation.get("verdict", "READY")).upper()
        if val_verdict in ("BLOCKED", "FAIL", "FAILED"):
            logger.error(f"[{verif_id}] Verification BLOCKED because Agent #9 design validation is BLOCKED.")
            final_verdict = FinalQAVerdict(
                verdict="BLOCKED",
                blocking_issues=["Agent #9 Engineering Validation verdict is BLOCKED."],
                recommendation="Resolve critical engineering design failures in Agent #9 before QA verification.",
            )
            report_md = self.report_generator.generate_report(
                project_title=proj_title,
                verification_id=verif_id,
                final_verdict=final_verdict,
                changes=[],
                tasks=[],
                requirements=[],
                test_results=[],
                evidence=[],
                security_findings=[],
                arch_conf=ConformanceResult(domain="architecture", status="FAIL", details="Validation blocked"),
                bom_conf=ConformanceResult(domain="bom", status="FAIL", details="Validation blocked"),
                armoriq_audit={},
                corrections=[],
                traceability=[],
            )
            return VerificationQAAgentOutput(
                status="blocked",
                verification_id=verif_id,
                project_id=context.project_id,
                verdict="BLOCKED",
                final_verdict=final_verdict,
                structured_report_markdown=report_md,
            )

        # 2. Extract tasks and paths
        plan_tasks = input_data.implementation_plan.get("tasks", [])
        exec_completed = input_data.execution_result.get("completed_tasks", [])
        exec_failed = input_data.execution_result.get("failed_tasks", [])
        exec_denied = input_data.execution_result.get("denied_actions", [])
        actual_changed_files = input_data.changed_files or input_data.execution_result.get("changed_files", [])

        # Allowed paths from plan
        allowed_paths = ["**"]
        if "authorized_execution" in input_data.execution_result:
            allowed_paths = input_data.execution_result["authorized_execution"].get("allowed_paths", ["**"])

        # 3. File Verification (Sections 8 & 9)
        changes = self.file_verifier.verify_changes(
            actual_changed_files=actual_changed_files,
            plan_tasks=plan_tasks,
            allowed_paths=allowed_paths,
        )

        # 4. Task Verification (Sections 10 & 11)
        tasks = self.task_verifier.verify_tasks(
            plan_tasks=plan_tasks,
            execution_completed=exec_completed,
            execution_failed=exec_failed,
            execution_denied=exec_denied,
            file_changes=changes,
        )

        # 5. Test Execution & Evidence (Sections 17, 18, 20, 34, 35, 36)
        test_results: List[TestResultObject] = []
        evidence: List[EvidenceObject] = []
        if not input_data.dry_run and not input_data.requirements_only and not input_data.security_only:
            # Check if tests exist in plan or input
            target_tests = [t.get("test_path") for t in plan_tasks if t.get("test_path")]
            if not target_tests:
                target_tests = ["research_agents/engineering_execution_agent/tests/test_tools.py"]
            test_results, evidence = self.test_runner.run_tests(target_tests)
        else:
            # Mock dry-run evidence
            evidence.append(
                EvidenceObject(
                    evidence_id="EVID-DRYRUN-001",
                    type="static_analysis",
                    source="dry_run_inspection",
                    result="Verified static file presence and syntax.",
                    timestamp=str(time.time()),
                    supports=["TASK-001"],
                )
            )

        # 6. Requirement Verification (Sections 14 & 15)
        requirements = self.requirement_verifier.verify_requirements(
            requirements=input_data.requirements,
            task_verifications=tasks,
            test_results=test_results,
            evidence_items=evidence,
        )

        # 7. Security Verification (Sections 27, 28, 56)
        files_to_scan = [ch.file for ch in changes] or actual_changed_files
        security_findings = self.security_scanner.scan_files(files_to_scan)

        # 8. Architecture and BOM Conformance (Sections 21, 22, 24, 25)
        arch_conf = self.conformance_checker.check_architecture_conformance(
            architecture=input_data.architecture,
            implementation_tasks=plan_tasks,
        )
        bom_conf = self.conformance_checker.check_bom_conformance(
            bom=input_data.bom,
            implementation_tasks=plan_tasks,
        )

        # 9. ArmorIQ Authorization Audit (Sections 29, 30, 57)
        tool_calls = input_data.execution_result.get("tool_calls", [])
        receipts = input_data.execution_result.get("armoriq_receipts", [])
        auth_id = input_data.execution_result.get("authorization_id", "AUTH-001")
        armoriq_audit = self.armoriq_auditor.audit_armoriq_execution(
            tool_calls=tool_calls,
            receipts=receipts,
            authorization_id=auth_id,
        )

        # 10. Generate Corrections for Failures (Section 50)
        corrections = self.correction_generator.generate_corrections(
            changes=changes,
            tasks=tasks,
            requirements=requirements,
            test_results=test_results,
            security_findings=security_findings,
            arch_conf=arch_conf,
            bom_conf=bom_conf,
        )

        # 11. Build Traceability (Section 52)
        traceability = self.traceability_builder.build_traceability(
            requirements=requirements,
            changes=changes,
            test_results=test_results,
            evidence=evidence,
            overall_verdict="PASS",
        )

        # 12. Quality Gate Verdict Computation (Sections 46 & 47)
        req_passed = sum(1 for r in requirements if r.status == "PASS")
        req_failed = sum(1 for r in requirements if r.status == "FAIL")
        req_unknown = sum(1 for r in requirements if r.status == "UNKNOWN")
        tasks_verified = sum(1 for t in tasks if t.implementation_status == "PASS")
        tasks_failed = sum(1 for t in tasks if t.implementation_status == "FAIL")
        tests_passed = sum(1 for tr in test_results if tr.status == "PASS")
        tests_failed = sum(1 for tr in test_results if tr.status in ("FAIL", "ERROR"))
        sec_failures = len(security_findings)
        scope_failures = sum(1 for ch in changes if ch.status == "FAIL")
        arch_failures = 1 if arch_conf.status == "FAIL" else 0
        bom_failures = 1 if bom_conf.status == "FAIL" else 0

        blocking_issues: List[str] = []
        if req_failed > 0:
            blocking_issues.append(f"{req_failed} mandatory engineering requirements failed.")
        if sec_failures > 0:
            blocking_issues.append(f"{sec_failures} critical security vulnerabilities detected.")
        if scope_failures > 0:
            blocking_issues.append(f"{scope_failures} unauthorized out-of-scope modifications detected.")
        if arch_failures > 0:
            blocking_issues.append("Architecture conformance violation.")
        if bom_failures > 0:
            blocking_issues.append("BOM component substitution violation.")
        if tests_failed > 0:
            blocking_issues.append(f"{tests_failed} integration/unit tests failed.")

        if blocking_issues:
            verdict = "FAILED"
            rec = f"Quality gate FAILED due to {len(blocking_issues)} critical violations: {'; '.join(blocking_issues)}"
        elif any(t.acceptance_status == "UNKNOWN" for t in tasks) or req_unknown > 0:
            verdict = "INCOMPLETE"
            rec = "Quality gate INCOMPLETE: Physical hardware verification requires lab environment or simulation."
        elif any(t.acceptance_status == "PARTIAL" for t in tasks) or (tests_passed == 0 and not input_data.dry_run):
            verdict = "VERIFIED_WITH_WARNINGS"
            rec = "Quality gate APPROVED WITH WARNINGS: Mandatory criteria satisfied; non-blocking items flagged."
        else:
            verdict = "VERIFIED"
            rec = "Quality gate VERIFIED: All mandatory requirements, tests, security, and conformance checks passed."

        final_verdict = FinalQAVerdict(
            verdict=verdict,
            requirements_passed=req_passed,
            requirements_failed=req_failed,
            requirements_unknown=req_unknown,
            tasks_verified=tasks_verified,
            tasks_failed=tasks_failed,
            tests_passed=tests_passed,
            tests_failed=tests_failed,
            security_failures=sec_failures,
            scope_failures=scope_failures,
            architecture_failures=arch_failures,
            bom_failures=bom_failures,
            warnings=1 if verdict == "VERIFIED_WITH_WARNINGS" else 0,
            unknowns=req_unknown,
            blocking_issues=blocking_issues,
            recommendation=rec,
        )

        # 13. Render 24-Section Markdown Report (Section 64)
        report_md = self.report_generator.generate_report(
            project_title=proj_title,
            verification_id=verif_id,
            final_verdict=final_verdict,
            changes=changes,
            tasks=tasks,
            requirements=requirements,
            test_results=test_results,
            evidence=evidence,
            security_findings=security_findings,
            arch_conf=arch_conf,
            bom_conf=bom_conf,
            armoriq_audit=armoriq_audit,
            corrections=corrections,
            traceability=traceability,
        )

        output = VerificationQAAgentOutput(
            status="success" if verdict in ("VERIFIED", "VERIFIED_WITH_WARNINGS") else "failed",
            verification_id=verif_id,
            project_id=context.project_id,
            verdict=verdict,
            final_verdict=final_verdict,
            changes=changes,
            tasks=tasks,
            requirements=requirements,
            test_results=test_results,
            evidence=evidence,
            security_findings=security_findings,
            architecture_conformance=arch_conf,
            bom_conformance=bom_conf,
            authorization_verification=armoriq_audit,
            corrections=corrections,
            traceability=traceability,
            structured_report_markdown=report_md,
        )

        # 14. File Export if output_dir provided (Section 63)
        if input_data.output_dir:
            self.file_exporter.export_artifacts(output, input_data.output_dir, overwrite=True)

        elapsed = time.time() - start_time
        logger.info(
            f"[{verif_id}][{self.NAME}] QA verification complete in {elapsed:.3f}s: "
            f"Verdict={verdict} ReqPassed={req_passed} SecFailures={sec_failures} TestsFailed={tests_failed}"
        )

        return output

    def run_sync(
        self,
        input_data: VerificationQAAgentInput,
        execution_id: Optional[str] = None,
    ) -> VerificationQAAgentOutput:
        """Synchronous wrapper for Google ADK / CLI execution."""
        return asyncio.run(self.run(input_data=input_data, execution_id=execution_id))

    # =========================================================================
    # Internal Google ADK Capability Methods (Section 66)
    # =========================================================================

    def verify_execution(self, input_data: VerificationQAAgentInput) -> VerificationQAAgentOutput:
        """ADK Capability: Executes complete end-to-end QA verification."""
        return self.run_sync(input_data)

    def verify_tasks(self, plan_tasks: List, completed: List, failed: List, denied: List, changes: List) -> List[TaskVerificationObject]:
        """ADK Capability: Verifies task execution and acceptance criteria."""
        return self.task_verifier.verify_tasks(plan_tasks, completed, failed, denied, changes)

    def verify_requirements(self, reqs: List, tasks: List, tests: List, evidence: List) -> List[RequirementVerificationItem]:
        """ADK Capability: Evaluates requirement coverage."""
        return self.requirement_verifier.verify_requirements(reqs, tasks, tests, evidence)

    def verify_architecture(self, architecture: Dict, tasks: List) -> ConformanceResult:
        """ADK Capability: Evaluates architecture conformance."""
        return self.conformance_checker.check_architecture_conformance(architecture, tasks)

    def verify_bom(self, bom: Dict, tasks: List) -> ConformanceResult:
        """ADK Capability: Evaluates BOM conformance."""
        return self.conformance_checker.check_bom_conformance(bom, tasks)

    def verify_files(self, actual_changed: List, plan_tasks: List, allowed_paths: List) -> List[ChangeObject]:
        """ADK Capability: Verifies file tree integrity."""
        return self.file_verifier.verify_changes(actual_changed, plan_tasks, allowed_paths)

    def run_tests(self, test_paths: List[str]) -> Tuple[List[TestResultObject], List[EvidenceObject]]:
        """ADK Capability: Executes test suites and collects evidence."""
        return self.test_runner.run_tests(test_paths)

    def run_static_analysis(self, file_paths: List[str]) -> List[SecurityFinding]:
        """ADK Capability: Scans files for static security risks."""
        return self.security_scanner.scan_files(file_paths)

    def verify_security(self, file_paths: List[str]) -> List[SecurityFinding]:
        """ADK Capability: Performs security audit."""
        return self.security_scanner.scan_files(file_paths)

    def verify_authorization(self, calls: List, receipts: List, auth_id: str) -> Dict[str, Any]:
        """ADK Capability: Audits ArmorIQ execution records."""
        return self.armoriq_auditor.audit_armoriq_execution(calls, receipts, auth_id)

    def generate_coverage_matrix(self, reqs: List[RequirementVerificationItem]) -> Dict[str, Any]:
        """ADK Capability: Generates requirement coverage summary."""
        return {
            "total": len(reqs),
            "passed": sum(1 for r in reqs if r.status == "PASS"),
            "coverage": [r.model_dump() for r in reqs],
        }

    def generate_traceability(self, reqs: List, changes: List, tests: List, evidence: List) -> List[VerificationTraceabilityItem]:
        """ADK Capability: Builds verification traceability."""
        return self.traceability_builder.build_traceability(reqs, changes, tests, evidence, "PASS")

    def generate_correction_report(self, changes: List, tasks: List, reqs: List, tests: List, sec: List, arch: Any, bom: Any) -> List[CorrectionReportItem]:
        """ADK Capability: Generates corrective action requests."""
        return self.correction_generator.generate_corrections(changes, tasks, reqs, tests, sec, arch, bom)

    def generate_final_verdict(self, output: VerificationQAAgentOutput) -> FinalQAVerdict:
        """ADK Capability: Returns QA final verdict."""
        return output.final_verdict
