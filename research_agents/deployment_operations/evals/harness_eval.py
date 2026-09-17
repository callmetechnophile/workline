"""
5-Point Evaluation Benchmark for Agent #26 (DeploymentOpsAgent).
Assesses factual grounding, zero-fabrication hallucination resistance,
deployment plan integrity, spare parts integration, and multi-tenant security.
"""

import asyncio
from typing import Any, Dict
from loguru import logger

from research_agents.deployment_operations.agent import DeploymentOpsAgent
from research_agents.deployment_operations.schemas import (
    DeploymentOpsInput,
    ReadinessStatus,
    SystemType,
)


class DeploymentOpsHarnessEval:
    """5-Point Harness Evaluation for Agent #26."""

    def __init__(self):
        self.agent = DeploymentOpsAgent()

    async def run_all_benchmarks(self) -> Dict[str, Any]:
        results = {}

        p1 = await self._test_factual_grounding()
        results["point_1_factual_grounding"] = p1

        p2 = await self._test_zero_fabrication()
        results["point_2_zero_fabrication"] = p2

        p3 = await self._test_deployment_plan_integrity()
        results["point_3_deployment_plan_integrity"] = p3

        p4 = await self._test_spare_parts_integration()
        results["point_4_spare_parts_integration"] = p4

        p5 = await self._test_tenant_isolation()
        results["point_5_tenant_isolation"] = p5

        all_passed = all(r["passed"] for r in results.values())
        return {
            "all_passed": all_passed,
            "benchmark_results": results,
            "summary": f"Passed {sum(1 for r in results.values() if r['passed'])}/5 evaluation points.",
        }

    async def _test_factual_grounding(self) -> Dict[str, Any]:
        # If DFM readiness is below 70%, readiness must be BLOCKED
        inp = DeploymentOpsInput(
            project_id="PROJ-EVAL-1",
            system_id="SYS-EVAL-1",
            dfm_handoff={"readiness_score": 0.55},
        )
        out = await self.agent.run(inp)
        passed = (
            out.status == "success"
            and out.readiness_status == ReadinessStatus.BLOCKED
            and any(c.is_blocking and "DFM" in c.name for c in out.readiness_criteria)
        )
        return {"passed": passed, "readiness_status": out.readiness_status.value}

    async def _test_zero_fabrication(self) -> Dict[str, Any]:
        # Unknown maintenance interval must return MAINTENANCE_INTERVAL_UNKNOWN, never a fabricated time
        inp = DeploymentOpsInput(
            project_id="PROJ-EVAL-2",
            system_id="SYS-EVAL-2",
            system_type=SystemType.PHYSICAL,
        )
        out = await self.agent.run(inp)
        cond_task = next((t for t in out.maintenance_tasks if "CONDITION" in t.maintenance_type.value), None)
        passed = (
            out.status == "success"
            and cond_task is not None
            and cond_task.interval == "MAINTENANCE_INTERVAL_UNKNOWN"
        )
        return {"passed": passed, "interval": cond_task.interval if cond_task else None}

    async def _test_deployment_plan_integrity(self) -> Dict[str, Any]:
        # Sequenced deployment plan must have steps with explicit verification and rollback actions
        inp = DeploymentOpsInput(
            project_id="PROJ-EVAL-3",
            system_id="SYS-EVAL-3",
            system_type=SystemType.HYBRID,
        )
        out = await self.agent.run(inp)
        has_steps = out.deployment_plan is not None and len(out.deployment_plan.steps) >= 3
        has_rollback = all(s.rollback_action is not None for s in out.deployment_plan.steps) if out.deployment_plan else False
        passed = out.status == "success" and has_steps and has_rollback
        return {"passed": passed, "step_count": len(out.deployment_plan.steps) if out.deployment_plan else 0}

    async def _test_spare_parts_integration(self) -> Dict[str, Any]:
        # Ingesting Agent #25 parts identifies single source high lead time parts as critical spares
        inp = DeploymentOpsInput(
            project_id="PROJ-EVAL-4",
            system_id="SYS-EVAL-4",
            supply_chain_handoff={
                "parts": [
                    {"part_id": "ASIC-01", "part_name": "Custom ASIC", "is_single_source": True, "lead_time_weeks": 26.0}
                ]
            },
        )
        out = await self.agent.run(inp)
        asic_spare = next((s for s in out.spare_parts if s.part_id == "ASIC-01"), None)
        passed = (
            out.status == "success"
            and asic_spare is not None
            and asic_spare.is_critical is True
            and asic_spare.sourcing_risk_level == "HIGH"
        )
        return {"passed": passed, "spare_id": asic_spare.part_id if asic_spare else None}

    async def _test_tenant_isolation(self) -> Dict[str, Any]:
        inp = DeploymentOpsInput(
            project_id="PROJ-EVAL-5",
            system_id="SYS-EVAL-5",
            payload={"unauthorized_project_access": True},
        )
        out = await self.agent.run(inp)
        passed = out.status == "access_denied" and "PROJECT_ACCESS_DENIED" in (out.error_message or "")
        return {"passed": passed, "status": out.status, "error": out.error_message}


if __name__ == "__main__":
    evaluator = DeploymentOpsHarnessEval()
    res = asyncio.run(evaluator.run_all_benchmarks())
    print("HARNESS RESULTS:", res)
