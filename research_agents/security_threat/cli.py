"""
CLI Entrypoint for SecurityThreatModelingAgent (Agent #22).
Run via: python -m security_threat [subcommand]
"""

import argparse
import asyncio
import json
import sys
from loguru import logger

from research_agents.security_threat.agent import SecurityThreatModelingAgent
from research_agents.security_threat.schemas import SecurityThreatModelingAgentInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="security_threat",
        description="SecurityThreatModelingAgent (Agent #22) CLI for WorkflowGuide AI",
    )
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # 1. assets
    p_assets = subparsers.add_parser("assets", help="List and discover system assets")
    p_assets.add_argument("--project", required=True, help="Project ID")

    # 2. surface
    p_surface = subparsers.add_parser("surface", help="Map attack surface and entry points")
    p_surface.add_argument("--project", required=True, help="Project ID")

    # 3. threats
    p_threats = subparsers.add_parser("threats", help="Generate and display threat register")
    p_threats.add_argument("--project", required=True, help="Project ID")

    # 4. threat
    p_threat = subparsers.add_parser("threat", help="Inspect a specific threat")
    p_threat.add_argument("--threat", required=True, help="Threat ID")
    p_threat.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 5. attack-path
    p_path = subparsers.add_parser("attack-path", help="Inspect attack paths for threat")
    p_path.add_argument("--threat", required=True, help="Threat ID")
    p_path.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 6. trust-boundaries
    p_tb = subparsers.add_parser("trust-boundaries", help="Display trust boundary crossings")
    p_tb.add_argument("--project", required=True, help="Project ID")

    # 7. controls
    p_ctrl = subparsers.add_parser("controls", help="List security controls and verification status")
    p_ctrl.add_argument("--project", required=True, help="Project ID")

    # 8. assess
    p_assess = subparsers.add_parser("assess", help="Assess threat likelihood, impact, and risk score")
    p_assess.add_argument("--threat", required=True, help="Threat ID")
    p_assess.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 9. mitigate
    p_mitigate = subparsers.add_parser("mitigate", help="Suggest security mitigations")
    p_mitigate.add_argument("--threat", required=True, help="Threat ID")
    p_mitigate.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 10. reassess
    p_reassess = subparsers.add_parser("reassess", help="Reassess threat model after engineering change")
    p_reassess.add_argument("--change", required=True, help="Change ID")
    p_reassess.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 11. impact
    p_impact = subparsers.add_parser("impact", help="Evaluate change security impact")
    p_impact.add_argument("--change", required=True, help="Change ID")
    p_impact.add_argument("--project", default="PROJECT-001", help="Project ID")

    # 12. tests
    p_tests = subparsers.add_parser("tests", help="Generate security test specifications")
    p_tests.add_argument("--project", required=True, help="Project ID")

    # 13. dashboard
    p_dash = subparsers.add_parser("dashboard", help="Show security posture dashboard")
    p_dash.add_argument("--project", required=True, help="Project ID")

    # 14. report
    p_report = subparsers.add_parser("report", help="Generate 22-section markdown report")
    p_report.add_argument("--project", required=True, help="Project ID")
    p_report.add_argument("--output", default="output/security_threat", help="Output directory")

    # 15. trace
    p_trace = subparsers.add_parser("trace", help="Trace threat to asset, control, and test")
    p_trace.add_argument("--threat", required=True, help="Threat ID")
    p_trace.add_argument("--project", default="PROJECT-001", help="Project ID")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(1)

    agent = SecurityThreatModelingAgent()
    project_id = getattr(args, "project", "PROJECT-001")

    op_map = {
        "assets": "discover_assets",
        "surface": "map_attack_surface",
        "threats": "model_threats",
        "threat": "assess_threat",
        "attack-path": "model_threats",
        "trust-boundaries": "map_attack_surface",
        "controls": "map_controls",
        "assess": "assess_threat",
        "mitigate": "propose_mitigations",
        "reassess": "reassess_security",
        "impact": "get_change_security_impact",
        "tests": "generate_security_tests",
        "dashboard": "evaluate_security_gate",
        "report": "export_artifacts",
        "trace": "model_threats",
    }

    op = op_map.get(args.subcommand, "full_threat_model")
    inp = SecurityThreatModelingAgentInput(
        project_id=project_id,
        operation=op,
        threat_id=getattr(args, "threat", None),
        change_id=getattr(args, "change", None),
        change_request={"change_id": getattr(args, "change", "CHG-01"), "project_id": project_id}
        if getattr(args, "change", None)
        else None,
        output_dir=getattr(args, "output", None),
    )

    out = agent.run_sync(inp)
    if args.subcommand == "report":
        print(out.structured_markdown_report)
    else:
        print(json.dumps(out.model_dump(), indent=2, default=str))


if __name__ == "__main__":
    main()
