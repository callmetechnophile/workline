"""
Authoritative 5-Point Evaluation Benchmark for Agent #25 (CostSupplyChainAgent).
Evaluates factual grounding, zero-fabrication hallucination resistance,
currency conversion precision, make-buy breakeven accuracy, and multi-tenant security.
"""

import asyncio
from typing import Any, Dict
from loguru import logger

from research_agents.cost_supply_chain.agent import CostSupplyChainAgent
from research_agents.cost_supply_chain.config import PRICE_UNKNOWN
from research_agents.cost_supply_chain.schemas import (
    CostSupplyChainInput,
    LifecycleStatus,
    PartCost,
)


class CostSupplyChainHarnessEval:
    """5-Point Harness Test for Agent #25."""

    def __init__(self):
        self.agent = CostSupplyChainAgent()

    async def run_all_benchmarks(self) -> Dict[str, Any]:
        results = {}

        # Point 1: Factual Grounding in BOM Parts
        p1 = await self._test_factual_grounding()
        results["point_1_factual_grounding"] = p1

        # Point 2: Zero Fabrication (Missing price -> PRICE_UNKNOWN, never made up)
        p2 = await self._test_zero_fabrication()
        results["point_2_zero_fabrication"] = p2

        # Point 3: Currency Normalization Consistency
        p3 = await self._test_currency_normalization()
        results["point_3_currency_normalization"] = p3

        # Point 4: Make-vs-Buy Breakeven Precision
        p4 = await self._test_make_buy_breakeven()
        results["point_4_make_buy_breakeven"] = p4

        # Point 5: Multi-Tenant Boundary Enforcement
        p5 = await self._test_tenant_isolation()
        results["point_5_tenant_isolation"] = p5

        all_passed = all(r["passed"] for r in results.values())
        return {
            "all_passed": all_passed,
            "benchmark_results": results,
            "summary": f"Passed {sum(1 for r in results.values() if r['passed'])}/5 evaluation points.",
        }

    async def _test_factual_grounding(self) -> Dict[str, Any]:
        parts = [
            PartCost(part_id="P1", part_name="Resistor", quantity_per_assembly=10, unit_cost=0.05),
            PartCost(part_id="P2", part_name="Capacitor", quantity_per_assembly=5, unit_cost=0.10),
        ]
        inp = CostSupplyChainInput(project_id="PROJ-EVAL-1", parts=parts)
        out = await self.agent.run(inp)
        expected_unit = (10 * 0.05) + (5 * 0.10)  # 1.00
        passed = out.status == "success" and out.rollup and abs(out.rollup.total_unit_cost - expected_unit) < 0.01
        return {"passed": passed, "expected_unit": expected_unit, "actual_unit": out.rollup.total_unit_cost if out.rollup else None}

    async def _test_zero_fabrication(self) -> Dict[str, Any]:
        parts = [
            PartCost(part_id="P1", part_name="Known Chip", quantity_per_assembly=1, unit_cost=5.00),
            PartCost(part_id="P2", part_name="Unpriced ASIC", quantity_per_assembly=1, unit_cost=None, price_status=PRICE_UNKNOWN),
        ]
        inp = CostSupplyChainInput(project_id="PROJ-EVAL-2", parts=parts)
        out = await self.agent.run(inp)
        passed = (
            out.status == "success"
            and out.rollup is not None
            and not out.rollup.is_cost_complete
            and out.rollup.unpriced_parts_count == 1
            and "P2" in out.rollup.unpriced_part_ids
        )
        return {"passed": passed, "unpriced_count": out.rollup.unpriced_parts_count if out.rollup else 0}

    async def _test_currency_normalization(self) -> Dict[str, Any]:
        parts = [
            PartCost(part_id="P_EUR", part_name="Euro Sensor", quantity_per_assembly=1, unit_cost=100.0, currency="EUR"),
        ]
        inp = CostSupplyChainInput(project_id="PROJ-EVAL-3", parts=parts, currency="USD")
        out = await self.agent.run(inp)
        # EUR rate is 1.08 -> 100 EUR = 108 USD
        passed = out.status == "success" and out.rollup and abs(out.rollup.total_unit_cost - 108.0) < 0.1
        return {"passed": passed, "converted_usd": out.rollup.total_unit_cost if out.rollup else None}

    async def _test_make_buy_breakeven(self) -> Dict[str, Any]:
        inp = CostSupplyChainInput(
            project_id="PROJ-EVAL-4",
            make_buy_params={
                "make_unit_cost": 20.0,
                "make_tooling_nre": 10000.0,
                "buy_unit_cost": 30.0,
                "buy_tooling_nre": 0.0,
            },
            target_volume=2000,
        )
        out = await self.agent.run(inp)
        # Breakeven = 10000 / (30 - 20) = 1000 units. Since target 2000 > 1000 -> recommendation MAKE
        passed = (
            out.status == "success"
            and out.make_buy is not None
            and out.make_buy.breakeven_volume == 1000.0
            and out.make_buy.recommendation.value == "MAKE"
        )
        return {
            "passed": passed,
            "breakeven": out.make_buy.breakeven_volume if out.make_buy else None,
            "recommendation": out.make_buy.recommendation.value if out.make_buy else None,
        }

    async def _test_tenant_isolation(self) -> Dict[str, Any]:
        inp = CostSupplyChainInput(
            project_id="PROJ-EVAL-5",
            payload={"unauthorized_project_access": True},
        )
        out = await self.agent.run(inp)
        passed = out.status == "access_denied" and "PROJECT_ACCESS_DENIED" in (out.error_message or "")
        return {"passed": passed, "status": out.status, "error": out.error_message}


if __name__ == "__main__":
    evaluator = CostSupplyChainHarnessEval()
    res = asyncio.run(evaluator.run_all_benchmarks())
    print("HARNESS RESULTS:", res)
