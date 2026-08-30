"""
CLI entry point for EngineeringOptimizationAgent (Agent #20).
Supports: create, run, candidates, pareto, compare, recommend, select, impact, reoptimize, report, --demo.
"""

import argparse
import asyncio
import json
from pathlib import Path
import sys
from typing import List, Optional

from research_agents.engineering_optimization.agent import EngineeringOptimizationAgent
from research_agents.engineering_optimization.providers.mock_provider import MockOptimizationProvider
from research_agents.engineering_optimization.schemas import OptimizationInput


def main(args: List[str] = None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="WorkflowGuide AI — EngineeringOptimizationAgent (Agent #20) CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Optimization commands")

    # run command
    p_run = subparsers.add_parser("run", help="Run full optimization cycle")
    p_run.add_argument("--project", type=str, default="proj_sar_drone_001", help="Project ID")
    p_run.add_argument("--candidates", type=int, default=10, help="Number of candidates")
    p_run.add_argument("--output", type=str, help="Output directory")

    # candidates command
    p_cand = subparsers.add_parser("candidates", help="List candidates for an optimization")
    p_cand.add_argument("--opt-id", type=str, required=True, help="Optimization ID")

    # pareto command
    p_pareto = subparsers.add_parser("pareto", help="Compute Pareto frontier")
    p_pareto.add_argument("--opt-id", type=str, required=True, help="Optimization ID")

    # recommend command
    p_rec = subparsers.add_parser("recommend", help="Get optimization recommendation")
    p_rec.add_argument("--opt-id", type=str, required=True, help="Optimization ID")

    # select command
    p_sel = subparsers.add_parser("select", help="Select a candidate (creates decision + change request)")
    p_sel.add_argument("--opt-id", type=str, required=True, help="Optimization ID")
    p_sel.add_argument("--candidate", type=str, required=True, help="Candidate ID")
    p_sel.add_argument("--user", type=str, default="engineer_001", help="User making the selection")
    p_sel.add_argument("--rationale", type=str, default="Best Pareto candidate", help="Selection rationale")

    # impact command
    p_imp = subparsers.add_parser("impact", help="Assess impact of candidate selection")
    p_imp.add_argument("--opt-id", type=str, required=True, help="Optimization ID")
    p_imp.add_argument("--candidate", type=str, required=True, help="Candidate ID")

    # reoptimize command
    p_reopt = subparsers.add_parser("reoptimize", help="Check if optimization is stale and needs re-run")
    p_reopt.add_argument("--opt-id", type=str, required=True, help="Optimization ID")
    p_reopt.add_argument("--bom-version", type=str, default="v2.0.0", help="Current BOM version")
    p_reopt.add_argument("--arch-version", type=str, default="v1.0.0", help="Current architecture version")

    # report command
    p_rep = subparsers.add_parser("report", help="Generate optimization report")
    p_rep.add_argument("--opt-id", type=str, required=True, help="Optimization ID")

    # demo flag
    parser.add_argument("--demo", action="store_true", help="Run optimization demonstration")

    parsed = parser.parse_args(args)
    agent = EngineeringOptimizationAgent(reasoning_provider=MockOptimizationProvider())

    if parsed.demo or not parsed.command:
        inp = OptimizationInput(project_id="proj_sar_drone_001")
        out = agent.run_optimization_cycle_sync(inp, n_candidates=8)
        _print_demo(out)

    elif parsed.command == "run":
        inp = OptimizationInput(project_id=parsed.project, output_dir=parsed.output)
        out = agent.run_optimization_cycle_sync(inp, n_candidates=parsed.candidates)
        _print_demo(out)

    elif parsed.command == "candidates":
        result = asyncio.run(agent.evaluate_candidates(parsed.opt_id))
        print(json.dumps(result, indent=2))

    elif parsed.command == "pareto":
        result = asyncio.run(agent.compute_pareto(parsed.opt_id))
        print(json.dumps(result, indent=2))

    elif parsed.command == "recommend":
        result = asyncio.run(agent.get_recommendation(parsed.opt_id))
        print(json.dumps(result, indent=2))

    elif parsed.command == "select":
        result = asyncio.run(
            agent.select_candidate(parsed.opt_id, parsed.candidate, parsed.user, parsed.rationale)
        )
        print(json.dumps(result, indent=2))

    elif parsed.command == "impact":
        result = asyncio.run(agent.assess_impact(parsed.opt_id, parsed.candidate))
        print(json.dumps(result, indent=2))

    elif parsed.command == "reoptimize":
        result = asyncio.run(
            agent.detect_reoptimization(parsed.opt_id, parsed.bom_version, parsed.arch_version)
        )
        print(json.dumps(result, indent=2))

    elif parsed.command == "report":
        result = asyncio.run(agent.generate_report(parsed.opt_id))
        print(result.get("report_markdown", ""))


def _print_demo(out):
    opt = out.optimization
    print(f"\nOptimization: {opt.optimization_id} ({opt.status})")
    print(f"Project: {opt.project_id}")
    print(f"Objectives: {[o.name for o in opt.objectives]}")
    print(f"Candidates: {len(out.candidates)} ({len([c for c in out.candidates if c.feasible])} feasible)")
    if out.pareto_frontier:
        print(f"Pareto Frontier: {len(out.pareto_frontier.points)} non-dominated points")
    print("\nTop Feasible Candidates:")
    feasible = [c for c in out.candidates if c.feasible][:5]
    for i, c in enumerate(feasible):
        obj_str = ", ".join(f"{k}={v}" for k, v in c.objective_values.items())
        print(f"  {i+1}. {c.candidate_id}: {obj_str}")
    infeasible = [c for c in out.candidates if not c.feasible]
    if infeasible:
        print(f"\nInfeasible Candidates (Hard Constraint Violations): {len(infeasible)}")
        for c in infeasible[:3]:
            print(f"  - {c.candidate_id}: {c.hard_constraint_violations}")


if __name__ == "__main__":
    main()
