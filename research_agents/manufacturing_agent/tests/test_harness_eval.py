"""Tests for Harness Evaluation Suite (Section 45)."""
from research_agents.manufacturing_agent.agent import ManufacturingDFMAgent
from research_agents.manufacturing_agent.evals.harness_eval import HarnessEvaluator

def test_harness_eval_benchmarks():
    agent = ManufacturingDFMAgent()
    evaluator = HarnessEvaluator()
    res = evaluator.run_eval(agent)
    assert res.total_benchmarks >= 5
    assert res.passed_benchmarks == res.total_benchmarks
    assert res.grounding_score == 100.0
    assert res.hallucination_resistance_score == 100.0
