"""
CLI Entrypoint for Manufacturing / DFM-DFA Agent (Agent #24).
Run via: python -m manufacturing_agent [subcommand]
"""

import argparse
import asyncio
import json
import sys
from loguru import logger

from research_agents.manufacturing_agent.agent import ManufacturingDFMAgent
from research_agents.manufacturing_agent.schemas import ManufacturingAgentInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manufacturing_agent",
        description="Manufacturing / DFM-DFA Agent (Agent #24) CLI for WorkflowGuide AI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    for cmd in [
        "analyze", "dfm", "dfa", "processes", "process", "tolerances", "materials",
        "tooling", "fixtures", "sequence", "inspection", "variation", "risks",
        "findings", "recommendations", "readiness", "impact", "reassess", "trace",
        "report", "dashboard"
    ]:
        p = subparsers.add_parser(cmd, help=f"Run {cmd} operation")
        p.add_argument("--project", default="PROJECT-001", help="Project ID")
        p.add_argument("--component", help="Component ID")
        p.add_argument("--output", default="output/manufacturing_agent", help="Output directory")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    agent = ManufacturingDFMAgent()
    project_id = getattr(args, "project", "PROJECT-001")

    op_map = {
        "dfm": "dfm_analysis",
        "dfa": "dfa_analysis",
        "processes": "process_selection",
        "process": "process_selection",
        "tolerances": "tolerance_analysis",
        "variation": "variation_analysis",
        "tooling": "tooling_analysis",
        "fixtures": "tooling_analysis",
        "sequence": "sequence_analysis",
        "inspection": "inspection_analysis",
        "readiness": "readiness_assessment",
        "reassess": "reassess_change",
        "report": "export_artifacts",
    }

    op = op_map.get(args.subcommand, "full_analysis")
    inp = ManufacturingAgentInput(
        project_id=project_id,
        operation=op,
        component_id=getattr(args, "component", None),
        output_dir=getattr(args, "output", None),
    )

    out = agent.run_sync(inp)
    if args.subcommand == "report":
        print(out.structured_markdown_report)
    else:
        print(json.dumps(out.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    main()
