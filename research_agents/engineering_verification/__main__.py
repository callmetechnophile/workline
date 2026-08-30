"""
CLI entry point for EngineeringVerificationAgent (Agent #18) (Sections 85–92).
Supports plan, run, status, coverage, matrix, evidence, impact, reverify, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_verification.agent import EngineeringVerificationAgent
from research_agents.engineering_verification.providers.mock_provider import MockVerificationProvider
from research_agents.engineering_verification.schemas import VerificationInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringVerificationAgent (Agent #18) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Verification commands")

    # status command
    p_stat = subparsers.add_parser("status", help="Get verification status and metrics")
    p_stat.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_stat.add_argument("--output", type=str, help="Output directory")

    # plan command
    p_plan = subparsers.add_parser("plan", help="Generate or inspect verification plan")
    p_plan.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # run command
    p_run = subparsers.add_parser("run", help="Execute authorized verification tests")
    p_run.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_run.add_argument("--test", type=str, default="TEST-SAR-001", help="Test ID")

    # coverage command
    p_cov = subparsers.add_parser("coverage", help="Show requirement verification coverage")
    p_cov.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # matrix command
    p_mat = subparsers.add_parser("matrix", help="View requirement-to-evidence matrix")
    p_mat.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # reverify command
    p_rev = subparsers.add_parser("reverify", help="Generate change re-verification scope")
    p_rev.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_rev.add_argument("--change", type=str, default="CHANGE-001", help="Change ID")
    p_rev.add_argument("--target", type=str, default="sensor_core", help="Target artifact")

    parser.add_argument("--demo", action="store_true", help="Run verification demonstration")

    parsed = parser.parse_args(args)
    agent = EngineeringVerificationAgent(reasoning_provider=MockVerificationProvider())

    if parsed.demo or not parsed.command:
        inp = VerificationInput(project_id="proj_sar_drone_001")
        out = agent.execute_verification_cycle_sync(inp)
        print(f"\nVerification Plan: {out.plan.verification_plan_id} (Project: {out.plan.project_id})")
        print(f"Coverage: {out.coverage.coverage_percentage}% ({out.coverage.verified_requirements}/{out.coverage.total_requirements} Verified)")
        print(f"Total Tests: {out.coverage.total_tests} | Passed: {out.coverage.passed_tests} | Failed: {out.coverage.failed_tests}")
        print("\nMeasurements Recorded:")
        for m in out.measurements:
            print(f"- {m.parameter}: {m.value} {m.unit} (Instrument: {m.instrument})")
        print("\nEvidence Packages Generated:")
        for ev in out.evidence:
            print(f"- [{ev.type}] {ev.evidence_id}: {ev.source} (Hash: {ev.hash[:12] if ev.hash else 'N/A'})")

    elif parsed.command == "status":
        inp = VerificationInput(project_id=parsed.project, output_dir=parsed.output)
        out = agent.execute_verification_cycle_sync(inp)
        print(f"\nProject: {parsed.project}")
        print(f"Requirements: {out.coverage.total_requirements}")
        print(f"Verified: {out.coverage.verified_requirements}")
        print(f"Failed: {out.coverage.failed_requirements}")
        print(f"Blocked: {out.coverage.blocked_requirements}")
        print(f"Evidence Count: {out.coverage.total_evidence}")
        print(f"Verification Coverage: {out.coverage.coverage_percentage}%")

    elif parsed.command == "coverage":
        cov = agent.get_coverage(parsed.project)
        print(f"\nVerification Coverage for {parsed.project}: {cov.coverage_percentage}%")
        print(f"Requirements Verified: {cov.verified_requirements}/{cov.total_requirements}")
        print(f"Tests Passed: {cov.passed_tests}/{cov.total_tests}")

    elif parsed.command == "matrix":
        inp = VerificationInput(project_id=parsed.project)
        out = agent.execute_verification_cycle_sync(inp)
        print(f"\nRequirement Verification Matrix: {parsed.project}\n")
        print(f"{'Requirement':<15} | {'Test ID':<15} | {'Method':<12} | {'Result':<10} | {'Status':<10}")
        print("-" * 75)
        for m in out.matrix:
            print(f"{m.requirement_id:<15} | {m.test_id:<15} | {m.method:<12} | {m.result:<10} | {m.status:<10}")

    elif parsed.command == "reverify":
        inv_t, inv_ev, reg = agent.reverify_change(parsed.target, parsed.project)
        print(f"\nRe-verification Scope for change on '{parsed.target}':")
        print(f"- Invalidated Tests: {', '.join(inv_t) if inv_t else 'None'}")
        print(f"- Invalidated Evidence: {', '.join(inv_ev) if inv_ev else 'None'}")
        print(f"- Scoped Regression Tests: {', '.join(reg) if reg else 'None'}")


if __name__ == "__main__":
    main()
