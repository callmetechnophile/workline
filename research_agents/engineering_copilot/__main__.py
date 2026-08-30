"""
CLI entry point for EngineeringCopilotAgent (Agent #15) (Sections 73–77).
Supports chat, ask, status, trace, impact, compare, timeline, health, next, and --demo.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_copilot.agent import EngineeringCopilotAgent
from research_agents.engineering_copilot.providers.mock_provider import MockCopilotProvider
from research_agents.engineering_copilot.schemas import CopilotInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringCopilotAgent (Agent #15) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Copilot commands")

    # ask command
    p_ask = subparsers.add_parser("ask", help="Ask an engineering question")
    p_ask.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_ask.add_argument("--question", type=str, required=True, help="Question to ask")
    p_ask.add_argument("--output", type=str, help="Directory to export response artifacts")

    # chat command
    p_chat = subparsers.add_parser("chat", help="Start interactive copilot conversation")
    p_chat.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    # trace command
    p_trace = subparsers.add_parser("trace", help="Trace requirement lineage")
    p_trace.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_trace.add_argument("--requirement", type=str, default="REQ-SAR-001", help="Requirement ID")

    # impact command
    p_impact = subparsers.add_parser("impact", help="Analyze component impact")
    p_impact.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_impact.add_argument("--component", type=str, default="500-0771-01", help="Component MPN")

    # compare command
    p_compare = subparsers.add_parser("compare", help="Compare BOM or architecture versions")
    p_compare.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_compare.add_argument("--version-a", type=str, default="V1", help="Version A")
    p_compare.add_argument("--version-b", type=str, default="V2", help="Version B")

    # status & next commands
    p_status = subparsers.add_parser("status", help="Get project status")
    p_status.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    p_next = subparsers.add_parser("next", help="Get next action from Agent #14")
    p_next.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")

    parser.add_argument("--demo", action="store_true", help="Run complete copilot QA demonstration")

    parsed = parser.parse_args(args)
    copilot = EngineeringCopilotAgent(reasoning_provider=MockCopilotProvider())

    if parsed.demo or not parsed.command:
        inp = CopilotInput(
            message="Why was the FLIR Lepton 3.5 sensor selected?",
            project_id="proj_sar_drone_001",
        )
        resp = copilot.answer_sync(inp)
        print(f"\nQuestion: {inp.message}\n")
        print(resp.answer)
        print(f"\nEvidence Grounded: {len(resp.evidence)} items")
        for ev in resp.evidence:
            print(f"- [{ev.source_type.upper()}] {ev.source_id}: {ev.relevance}")

    elif parsed.command == "ask":
        inp = CopilotInput(
            message=parsed.question,
            project_id=parsed.project,
            output_dir=parsed.output,
        )
        resp = copilot.answer_sync(inp)
        print(f"\nQuestion: {parsed.question}\n")
        print(resp.answer)

    elif parsed.command == "trace":
        resp = copilot.trace_requirement(parsed.requirement, parsed.project)
        print(f"\nRequirement Trace: {parsed.requirement}\n")
        print(resp.answer)

    elif parsed.command == "impact":
        resp = copilot.trace_component(parsed.component, parsed.project)
        print(f"\nComponent Impact: {parsed.component}\n")
        print(resp.answer)

    elif parsed.command == "compare":
        resp = copilot.compare_versions(parsed.version_a, parsed.version_b, parsed.project)
        print(f"\nComparison: {parsed.version_a} vs {parsed.version_b}\n")
        print(resp.answer)

    elif parsed.command == "status":
        resp = copilot.get_project_status(parsed.project)
        print(f"\nProject Status: {parsed.project}\n")
        print(resp.answer)

    elif parsed.command == "next":
        resp = copilot.get_next_action(parsed.project)
        print(f"\nRecommended Next Action: {parsed.project}\n")
        print(resp.answer)


if __name__ == "__main__":
    main()
