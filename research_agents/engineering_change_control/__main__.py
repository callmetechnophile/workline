"""
CLI entry point for EngineeringChangeControlAgent (Agent #16) (Sections 50–56).
Supports create, analyze, show, impact, diff, approve, rollback, history, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_change_control.agent import EngineeringChangeControlAgent
from research_agents.engineering_change_control.providers.mock_provider import MockChangeControlProvider
from research_agents.engineering_change_control.schemas import ChangeControlInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringChangeControlAgent (Agent #16) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Change Control commands")

    # create command
    p_create = subparsers.add_parser("create", help="Create an engineering change request")
    p_create.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_create.add_argument("--type", type=str, default="COMPONENT_CHANGE", help="Change type")
    p_create.add_argument("--target", type=str, default="500-0771-01", help="Target artifact")
    p_create.add_argument("--title", type=str, default="Replace thermal sensor candidate", help="Title")
    p_create.add_argument("--description", type=str, default="Replace FLIR Lepton 2.5 with 3.5", help="Description")
    p_create.add_argument("--output", type=str, help="Output directory")

    # impact command
    p_impact = subparsers.add_parser("impact", help="Inspect impact of a change")
    p_impact.add_argument("--change", type=str, required=True, help="Change ID")

    # approve command
    p_approve = subparsers.add_parser("approve", help="Approve a change request")
    p_approve.add_argument("--change", type=str, required=True, help="Change ID")
    p_approve.add_argument("--approver", type=str, default="lead_engineer_002", help="Approver ID")

    # rollback command
    p_roll = subparsers.add_parser("rollback", help="Execute forward rollback versioning")
    p_roll.add_argument("--artifact", type=str, required=True, help="Artifact ID")
    p_roll.add_argument("--target-version", type=str, default="v1.0.0", help="Target version")
    p_roll.add_argument("--current-version", type=str, default="v2.0.0", help="Current version")
    p_roll.add_argument("--approved-by", type=str, default="lead_engineer_002", help="Approver ID")

    parser.add_argument("--demo", action="store_true", help="Run change control demonstration")

    parsed = parser.parse_args(args)
    agent = EngineeringChangeControlAgent(reasoning_provider=MockChangeControlProvider())

    if parsed.demo or not parsed.command:
        inp = ChangeControlInput(
            project_id="proj_sar_drone_001",
            change_type="COMPONENT_CHANGE",
            title="Replace FLIR Lepton 2.5 with 3.5 Core",
            description="Upgrade sensor core to 160x120 radiometric thermal imager.",
            target_artifact="500-0771-01",
        )
        out = agent.process_change_request_sync(inp)
        print(f"\nChange Request Created: {out.change_request.change_id}")
        print(f"Severity: {out.change_request.severity}")
        print(f"Status: {out.change_request.status}")
        print(f"\nDirect Impact: {len(out.impact.direct_impact)} items")
        for item in out.impact.direct_impact:
            print(f"- {item}")
        print(f"\nRevalidation Stages Required: {', '.join(out.impact.revalidation_required)}")
        print(f"Human Approval Required: {out.impact.human_approval_required}")

    elif parsed.command == "create":
        inp = ChangeControlInput(
            project_id=parsed.project,
            change_type=parsed.type,
            title=parsed.title,
            description=parsed.description,
            target_artifact=parsed.target,
            output_dir=parsed.output,
        )
        out = agent.process_change_request_sync(inp)
        print(f"\nChange Request Created: {out.change_request.change_id}")
        print(f"Status: {out.change_request.status}")
        print(f"Severity: {out.change_request.severity}")

    elif parsed.command == "rollback":
        roll, new_ver = agent.execute_rollback(
            artifact_id=parsed.artifact,
            target_version=parsed.target_version,
            current_version=parsed.current_version,
            approved_by=parsed.approved_by,
        )
        print(f"\nRollback Executed: {roll.rollback_id}")
        print(f"New Version Created: {new_ver.version} (Supersedes {new_ver.supersedes})")


if __name__ == "__main__":
    main()
