"""
Unit tests for ConformanceChecker service (Sections 21, 22, 24, 25).
"""

from research_agents.verification_qa_agent.services.conformance_checker import ConformanceChecker


def test_conformance_checker_architecture_and_bom():
    checker = ConformanceChecker()

    # Valid tasks
    valid_tasks = [{"task_id": "TASK-01", "title": "Implement valid sensor flow"}]
    arch_res = checker.check_architecture_conformance({}, valid_tasks)
    bom_res = checker.check_bom_conformance({}, valid_tasks)

    assert arch_res.status == "PASS"
    assert bom_res.status == "PASS"

    # Tasks with architecture bypass and unapproved substitute
    invalid_tasks = [
        {"task_id": "TASK-02", "title": "Bypass preprocessor layer directly to AI model"},
        {"task_id": "TASK-03", "title": "Use unapproved substitute component instead of FLIR"},
    ]

    arch_res_inv = checker.check_architecture_conformance({}, invalid_tasks)
    bom_res_inv = checker.check_bom_conformance({}, invalid_tasks)

    assert arch_res_inv.status == "FAIL"
    assert len(arch_res_inv.violations) == 1

    assert bom_res_inv.status == "FAIL"
    assert len(bom_res_inv.violations) == 1
