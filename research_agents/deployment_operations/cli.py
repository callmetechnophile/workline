"""
Command-line interface for Agent #26 (DeploymentOpsAgent).
"""

import argparse
import asyncio
import json
import sys
from research_agents.deployment_operations.agent import DeploymentOpsAgent
from research_agents.deployment_operations.evals.harness_eval import DeploymentOpsHarnessEval
from research_agents.deployment_operations.schemas import DeploymentOpsInput, SystemType


def parse_args():
    parser = argparse.ArgumentParser(
        description="Agent #26: Deployment & Operations Agent CLI"
    )
    parser.add_argument("--project-id", type=str, default="DEMO-PROJ", help="Target project ID")
    parser.add_argument("--system-id", type=str, default="SYS-PRIMARY", help="Target system ID")
    parser.add_argument("--system-type", type=str, default="HYBRID", help="System type (PHYSICAL, SOFTWARE, HYBRID, etc.)")
    parser.add_argument("--environment", type=str, default="production", help="Target environment")
    parser.add_argument("--eval", action="store_true", help="Run 5-point evaluation benchmark")
    parser.add_argument("--output-json", action="store_true", help="Output full JSON payload")
    return parser.parse_args()


async def async_main():
    args = parse_args()
    agent = DeploymentOpsAgent()

    if args.eval:
        evaluator = DeploymentOpsHarnessEval()
        results = await evaluator.run_all_benchmarks()
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["all_passed"] else 1)

    stype = SystemType.HYBRID
    try:
        stype = SystemType(args.system_type.upper())
    except ValueError:
        pass

    inp = DeploymentOpsInput(
        project_id=args.project_id,
        system_id=args.system_id,
        system_type=stype,
        environment=args.environment,
    )
    out = await agent.run(inp)

    if args.output_json:
        print(json.dumps(out.model_dump(), indent=2))
    else:
        print(f"Agent #26 Status:            {out.status}")
        print(f"System ID:                   {out.system_id} ({out.system_type.value})")
        print(f"Deployment Readiness:        {out.readiness_status.value}")
        if out.deployment_plan:
            print(f"Deployment Steps:            {len(out.deployment_plan.steps)} steps planned")
        if out.commissioning_plan:
            print(f"Commissioning Tests:         {len(out.commissioning_plan.tests)} tests scheduled")
        print(f"Health Metrics Configured:   {len(out.health_metrics)}")
        print(f"Maintenance Tasks:           {len(out.maintenance_tasks)}")
        print(f"Critical Spares:             {len(out.spare_parts)}")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
