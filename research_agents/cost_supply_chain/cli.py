"""
Command-line interface for Agent #25 (CostSupplyChainAgent).
"""

import argparse
import asyncio
import json
import sys
from loguru import logger

from research_agents.cost_supply_chain.agent import CostSupplyChainAgent
from research_agents.cost_supply_chain.evals.harness_eval import CostSupplyChainHarnessEval
from research_agents.cost_supply_chain.schemas import CostSupplyChainInput


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agent #25: Cost & Supply Chain Agent CLI"
    )
    parser.add_argument("--project-id", type=str, default="DEMO-PROJ", help="Target project ID")
    parser.add_argument("--volume", type=int, default=1000, help="Target production volume")
    parser.add_argument("--currency", type=str, default="USD", help="Target currency code (USD, EUR, etc.)")
    parser.add_argument("--eval", action="store_true", help="Run 5-point evaluation benchmark")
    parser.add_argument("--output-json", action="store_true", help="Output full JSON payload")
    return parser.parse_args()


async def async_main():
    args = parse_args()
    agent = CostSupplyChainAgent()

    if args.eval:
        evaluator = CostSupplyChainHarnessEval()
        results = await evaluator.run_all_benchmarks()
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["all_passed"] else 1)

    inp = CostSupplyChainInput(
        project_id=args.project_id,
        target_volume=args.volume,
        currency=args.currency,
    )
    out = await agent.run(inp)

    if args.output_json:
        print(json.dumps(out.model_dump(), indent=2))
    else:
        print(f"Agent #25 Status: {out.status}")
        if out.rollup:
            print(f"Total BOM Unit Cost: ${out.rollup.total_unit_cost or 0.0:.2f} {out.rollup.currency}")
            print(f"Total Tooling NRE:   ${out.rollup.total_tooling_nre:.2f} {out.rollup.currency}")
            print(f"Cost Complete:       {out.rollup.is_cost_complete} ({out.rollup.unpriced_parts_count} unpriced)")
        print(f"Supply Chain Risks:  {len(out.risks)} identified")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
