"""
Unit tests for ComparisonEngine (Sections 23 & 33).
"""

from research_agents.engineering_copilot.services.comparison_engine import ComparisonEngine


def test_comparison_engine_bom_and_architecture():
    engine = ComparisonEngine()

    bom_diff = engine.compare_boms({}, {})
    assert bom_diff.comparison_type == "BOM_COMPARISON"
    assert len(bom_diff.added) > 0
    assert len(bom_diff.removed) > 0
    assert bom_diff.revalidation_required is True

    arch_diff = engine.compare_architectures({}, {})
    assert arch_diff.comparison_type == "ARCHITECTURE_COMPARISON"
    assert len(arch_diff.added) > 0
    assert arch_diff.revalidation_required is True
