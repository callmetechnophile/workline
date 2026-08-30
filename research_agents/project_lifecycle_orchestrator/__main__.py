"""
CLI entry point for ProjectLifecycleOrchestrator (Agent #14) (Sections 60–66).
Supports status, next, run, pause, resume, stop, health, blockers, history, impact, approve, reject, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.project_lifecycle_orchestrator.agent import ProjectLifecycleOrchestrator
from research_agents.project_lifecycle_orchestrator.providers.mock_provider import MockOrchestratorProvider
from research_agents.project_lifecycle_orchestrator.schemas import OrchestrationInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — ProjectLifecycleOrchestrator (Agent #14) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Orchestrator commands")

    # status command (Section 60)
    p_status = subparsers.add_parser("status", help="Inspect project state and next action")
    p_status.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")

    # next command (Section 61)
    p_next = subparsers.add_parser("next", help="Determine next valid engineering action")
    p_next.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")
    p_next.add_argument("--qa-status", type=str, default="VERIFIED", help="Latest QA status (VERIFIED/FAILED)")
    p_next.add_argument("--failure-type", type=str, default=None, help="Failure type if QA failed")

    # run command (Section 62)
    p_run = subparsers.add_parser("run", help="Run full closed-loop orchestration cycle")
    p_run.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")
    p_run.add_argument("--output", type=str, help="Directory to export orchestration artifacts")

    # health command (Section 58)
    p_health = subparsers.add_parser("health", help="Check project engineering health")
    p_health.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")

    # blockers command
    p_blockers = subparsers.add_parser("blockers", help="List active workflow blockers")
    p_blockers.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")

    # history command
    p_history = subparsers.add_parser("history", help="List decision history")
    p_history.add_argument("--project", type=str, default="PROJECT-001", help="Project ID")

    # impact command
    p_impact = subparsers.add_parser("impact", help="Determine change revalidation scope")
    p_impact.add_argument("--change-type", type=str, default="COMPONENT", help="Change type (COMPONENT/ARCHITECTURE/DOCUMENTATION)")
    p_impact.add_argument("--artifact", type=str, default="500-0771-01", help="Artifact ID")

    # approve & reject commands (Section 66)
    p_approve = subparsers.add_parser("approve", help="Approve human decision request")
    p_approve.add_argument("request_id", type=str, help="Human Request ID")

    p_reject = subparsers.add_parser("reject", help="Reject human decision request")
    p_reject.add_argument("request_id", type=str, help="Human Request ID")

    parser.add_argument("--demo", action="store_true", help="Run complete SAR drone orchestration demo")

    parsed = parser.parse_args(args)
    orchestrator = ProjectLifecycleOrchestrator(reasoning_provider=MockOrchestratorProvider())

    if parsed.demo or parsed.command == "run" or (not parsed.command and not parsed.demo):
        out_dir = getattr(parsed, "output", None)
        inp = OrchestrationInput(
            project_id=getattr(parsed, "project", "PROJECT-001"),
            user_id="user_001",
            output_dir=out_dir,
        )
        out = orchestrator.run_sync(inp)
        print(f"\nProject:\n{out.run.project_id}\n")
        print(f"State:\n{out.run.current_state}\n")
        print(f"Health:\n{out.health.health.upper()}\n")
        print(f"Completed:\n{out.run.completed}\n")
        print(f"Next Action:\n{out.next_action.action_type} via {out.next_action.target_agent}\n")
        print(f"Reason:\n{out.next_action.reason}\n")
        print(f"Authorization Required:\n{out.next_action.required_authorization}\n")

    elif parsed.command == "status":
        inp = OrchestrationInput(project_id=parsed.project, user_id="user_001")
        out = orchestrator.run_sync(inp)
        print(f"\nProject:\n{parsed.project}\n")
        print(f"State:\n{out.run.current_state}\n")
        print(f"Health:\n{out.health.health.upper()}\n")
        print(f"Completed:\n{out.run.completed}\n")
        print(f"Next Action:\n{out.next_action.action_type} ({out.next_action.target_agent})\n")

    elif parsed.command == "next":
        inp = OrchestrationInput(project_id=parsed.project, user_id="user_001")
        out = orchestrator.run_sync(
            inp,
            qa_status=parsed.qa_status,
            last_failure_type=parsed.failure_type,
        )
        print(f"\nCurrent State:\n{out.run.current_state}\n")
        print(f"Latest Result:\n{parsed.qa_status}\n")
        if parsed.failure_type:
            print(f"Failure:\n{parsed.failure_type}\n")
        print(f"Recommended Next Action:\n{out.next_action.action_type}\n")
        print(f"Target:\n{out.next_action.target_agent}\n")
        print(f"Human Approval:\n{'YES' if out.next_action.human_approval_required else 'NO'}\n")

    elif parsed.command == "health":
        health = orchestrator.get_project_health(parsed.project)
        print(f"\nProject Health: {parsed.project}")
        print(f"Health Status: {health.health.upper()}")
        print(f"Requirements: {health.requirements_status}")
        print(f"Architecture: {health.architecture_status}")
        print(f"BOM: {health.bom_status}")
        print(f"QA: {health.qa_status}\n")

    elif parsed.command == "blockers":
        blockers = orchestrator.evaluate_blockers(parsed.project)
        print(f"\nActive Blockers: {parsed.project}")
        if not blockers:
            print("No active blockers.")
        else:
            for b in blockers:
                print(f"- [{b.severity.upper()}] {b.type}: {b.resolution}")

    elif parsed.command == "impact":
        plan = orchestrator.determine_revalidation_scope(parsed.change_type, parsed.artifact)
        print(f"\nRevalidation Scope for {parsed.artifact} ({parsed.change_type}):")
        print(f"Required Stages: {', '.join(plan.required_stages) if plan.required_stages else 'NONE (Zero engineering revalidation)'}")
        print(f"Human Approval Needed: {plan.human_approval_needed}\n")

    elif parsed.command == "approve":
        req = orchestrator.human_manager.approve_request(parsed.request_id)
        if req:
            print(f"\nHuman Request [{parsed.request_id}] APPROVED.")
        else:
            print(f"\nRequest [{parsed.request_id}] not found.")

    elif parsed.command == "reject":
        req = orchestrator.human_manager.reject_request(parsed.request_id)
        if req:
            print(f"\nHuman Request [{parsed.request_id}] REJECTED.")
        else:
            print(f"\nRequest [{parsed.request_id}] not found.")


if __name__ == "__main__":
    main()
