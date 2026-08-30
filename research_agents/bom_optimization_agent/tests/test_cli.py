"""
Unit tests for BOMOptimizationAgent CLI development mode (Section 46).
"""

from research_agents.bom_optimization_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--project", "CLI Test SAR Drone", "--destination", "Bengaluru, Karnataka, India"])
    captured = capsys.readouterr().out

    assert "Project:" in captured
    assert "BOM Items:" in captured
    assert "Feasible Items:" in captured
    assert "Suppliers Evaluated:" in captured
    assert "Recommended Suppliers:" in captured
    assert "Orders:" in captured
    assert "Product Cost:" in captured
    assert "Shipping:" in captured
    assert "Known Landed Cost:" in captured
    assert "+ Technical compatibility preserved" in captured
    assert "+ Procurement optimized" in captured
    assert "+ Shipping calculated where data exists" in captured
    assert "+ Alternatives evaluated" in captured
    assert "+ Traceability generated" in captured
