"""
CLI entry point for EngineeringComplianceAgent (Agent #17) (Sections 80–86).
Supports check, matrix, component, bom, report, waiver, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_compliance.agent import EngineeringComplianceAgent
from research_agents.engineering_compliance.providers.mock_provider import MockComplianceProvider
from research_agents.engineering_compliance.schemas import ComplianceInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringComplianceAgent (Agent #17) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Compliance commands")

    # check command
    p_check = subparsers.add_parser("check", help="Evaluate project compliance and gate status")
    p_check.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_check.add_argument("--output", type=str, help="Output directory")

    # matrix command
    p_matrix = subparsers.add_parser("matrix", help="View requirement-to-compliance matrix")
    p_matrix.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # component command
    p_comp = subparsers.add_parser("component", help="Evaluate component compliance")
    p_comp.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_comp.add_argument("--component", type=str, default="500-0771-01", help="Component MPN")

    # waiver command
    p_waiv = subparsers.add_parser("waiver", help="Create an approved temporary waiver")
    p_waiv.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_waiv.add_argument("--rule", type=str, default="RULE-ELEC-01", help="Rule ID")
    p_waiv.add_argument("--artifact", type=str, default="component:500-0771-01", help="Artifact ID")
    p_waiv.add_argument("--reason", type=str, default="Temporary lab supply voltage variance", help="Reason")
    p_waiv.add_argument("--approved-by", type=str, default="safety_officer_001", help="Approver ID")

    parser.add_argument("--demo", action="store_true", help="Run compliance gate demonstration")

    parsed = parser.parse_args(args)
    agent = EngineeringComplianceAgent(reasoning_provider=MockComplianceProvider())

    if parsed.demo or not parsed.command:
        inp = ComplianceInput(project_id="proj_sar_drone_001")
        out = agent.evaluate_compliance_sync(inp)
        print(f"\nProject Compliance Summary: {out.summary.project_id}")
        print(f"Overall Status: {out.summary.status}")
        print(f"Gate Outcome: {out.summary.gate} (Blocking: {out.summary.blocking})")
        print(f"\nTotal Checks: {out.summary.total_checks} | Passed: {out.summary.passed} | Failed: {out.summary.failed}")
        print("\nCompliance Results:")
        for r in out.results:
            print(f"- [{r.status}] {r.rule_id} ({r.domain}): {r.description}")

    elif parsed.command == "check":
        inp = ComplianceInput(project_id=parsed.project, output_dir=parsed.output)
        out = agent.evaluate_compliance_sync(inp)
        print(f"\nProject: {parsed.project}")
        print(f"Status: {out.summary.status}")
        print(f"Gate: {out.summary.gate}")
        print(f"Critical Failures: {out.summary.critical_failures}")
        print(f"Warnings: {out.summary.warnings}")

    elif parsed.command == "matrix":
        inp = ComplianceInput(project_id=parsed.project)
        out = agent.evaluate_compliance_sync(inp)
        print(f"\nTraceability Matrix: {parsed.project}\n")
        print(f"{'Requirement':<15} | {'Rule':<15} | {'Artifact':<25} | {'Result':<10} | {'Severity':<10}")
        print("-" * 80)
        for m in out.matrix:
            print(f"{m.requirement_id:<15} | {m.rule_id:<15} | {m.artifact_id:<25} | {m.result:<10} | {m.severity:<10}")

    elif parsed.command == "waiver":
        waiver = agent.create_waiver_request(
            project_id=parsed.project,
            rule_id=parsed.rule,
            artifact_id=parsed.artifact,
            reason=parsed.reason,
            risk="Low temporary operational variance",
            approved_by=parsed.approved_by,
        )
        print(f"\nWaiver Created: {waiver.waiver_id}")
        print(f"Rule: {waiver.rule_id} for {waiver.artifact_id}")
        print(f"Expires At: {waiver.expires_at}")


if __name__ == "__main__":
    main()
