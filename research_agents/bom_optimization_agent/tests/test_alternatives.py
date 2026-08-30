"""
Unit tests for AlternativeEvaluator (Sections 10 & 18).
"""

from research_agents.bom_optimization_agent.services.alternative_evaluator import AlternativeEvaluator


def test_alternative_evaluator():
    evaluator = AlternativeEvaluator()

    alts = [
        {"alternative_id": "ALT-01", "part_number": "STM32", "compatibility": "electrically_compatible"},
        {"alternative_id": "ALT-02", "part_number": "RPi5", "compatibility": "architecture_alternative"},
        {"alternative_id": "ALT-03", "part_number": "Custom", "compatibility": "partial_compatibility"},
    ]

    res = evaluator.evaluate_alternatives(alts, [])
    assert len(res) == 3
    assert res[0]["requires_engineering_approval"] is False
    assert res[1]["requires_engineering_approval"] is True
    assert res[2]["requires_engineering_approval"] is True
