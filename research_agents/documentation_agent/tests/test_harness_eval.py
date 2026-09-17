import pytest
from research_agents.documentation_agent.evals.harness_eval import run_eval


def test_harness_eval_all_pass():
    result = run_eval()
    assert result["all_passed"], f"Harness eval failed: {result}"
