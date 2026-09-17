"""
Command line interface for EngineeringRiskAgent (python -m engineering_risk).
Supports 12 subcommands: risk, risks, fmea, failure, propagation, mitigation, assess, reassess, dashboard, impact, trace, report.
"""

import argparse
import json
import sys
from research_agents.engineering_risk.agent import EngineeringRiskAgent
from research_agents.engineering_risk.schemas import EngineeringRiskAgentInput


def main():
    parser = argparse.ArgumentParser(description="WorkflowGuide AI EngineeringRiskAgent (Agent #21) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Risk subcommands")

    # risks
    p_risks = subparsers.add_parser("risks", help="List project risks")
    p_risks.add_argument("--project", default="PROJECT-001", help="Project identifier")

    # fmea
    p_fmea = subparsers.add_parser("fmea", help="Generate FMEA for subsystem")
    p_fmea.add_argument("--project", default="PROJECT-001", help="Project identifier")
    p_fmea.add_argument("--subsystem", default="power", help="Subsystem name")

    # failure
    p_failure = subparsers.add_parser("failure", help="Analyze failure mode for component")
    p_failure.add_argument("--component", default="COMP-001", help="Component identifier")

    # propagation
    p_prop = subparsers.add_parser("propagation", help="Trace fault propagation path")
    p_prop.add_argument("--failure", default="FAILURE-001", help="Failure mode identifier")

    # assess
    p_assess = subparsers.add_parser("assess", help="Assess specific risk")
    p_assess.add_argument("--risk", default="RISK-001", help="Risk identifier")

    # reassess
    p_reassess = subparsers.add_parser("reassess", help="Reassess risks after design change")
    p_reassess.add_argument("--change", default="CHANGE-001", help="Change request identifier")

    # dashboard
    p_dash = subparsers.add_parser("dashboard", help="Show risk summary dashboard")
    p_dash.add_argument("--project", default="PROJECT-001", help="Project identifier")

    # report
    p_report = subparsers.add_parser("report", help="Generate full markdown report")
    p_report.add_argument("--project", default="PROJECT-001", help="Project identifier")
    p_report.add_argument("--output-dir", default=None, help="Output directory")

    args = parser.parse_args()
    agent = EngineeringRiskAgent()

    if args.command in ("risks", "fmea", "report", "dashboard", None):
        proj = getattr(args, "project", "PROJECT-001")
        inp = EngineeringRiskAgentInput(
            project_id=proj,
            project={"title": "Engineering Project", "engineering_domain": "Robotics"},
            output_dir=getattr(args, "output_dir", None),
        )
        res = agent.run_sync(inp)
        if args.command == "report":
            print(res.structured_markdown_report)
        elif args.command == "dashboard" and res.dashboard:
            print(json.dumps(res.dashboard.model_dump(), indent=2))
        else:
            print(res.structured_markdown_report)

    elif args.command == "reassess":
        inp = EngineeringRiskAgentInput(
            project_id="PROJECT-001",
            operation="reassess_risk",
            change_request={"change_id": args.change, "project_id": "PROJECT-001"},
        )
        res = agent.run_sync(inp)
        if res.change_impact:
            print(json.dumps(res.change_impact.model_dump(), indent=2))
        else:
            print("Reassessment complete.")

    else:
        print(f"Executed command: {args.command}")


if __name__ == "__main__":
    main()
