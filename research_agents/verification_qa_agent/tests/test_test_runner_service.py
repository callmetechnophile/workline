"""
Unit tests for TestRunnerService (Sections 17, 18, 20).
"""

from research_agents.verification_qa_agent.services.test_runner_service import TestRunnerService


def test_test_runner_service_execution():
    runner = TestRunnerService()
    test_results, evidence = runner.run_tests(
        test_paths=["research_agents/engineering_execution_agent/tests/test_tools.py"],
        timeout_sec=30,
    )

    assert len(test_results) == 1
    assert test_results[0].status == "PASS"
    assert len(evidence) == 1
    assert evidence[0].type == "test"
