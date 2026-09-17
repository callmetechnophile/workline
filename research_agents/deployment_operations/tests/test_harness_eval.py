"""Tests running the 5-point evaluation harness."""
import pytest
from research_agents.deployment_operations.evals.harness_eval import DeploymentOpsHarnessEval


@pytest.mark.asyncio
async def test_harness_eval_all_pass():
    evaluator = DeploymentOpsHarnessEval()
    res = await evaluator.run_all_benchmarks()
    assert res["all_passed"] is True
    for pt, detail in res["benchmark_results"].items():
        assert detail["passed"] is True, f"Benchmark {pt} failed"
