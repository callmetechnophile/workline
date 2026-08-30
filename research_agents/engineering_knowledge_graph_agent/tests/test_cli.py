"""
Unit tests for EngineeringKnowledgeGraphAgent CLI development mode (Sections 73–77).
"""

from research_agents.engineering_knowledge_graph_agent.__main__ import main


def test_cli_demo_and_commands(capsys):
    # 1. Test Demo / Ingest
    main(["--demo"])
    captured = capsys.readouterr().out
    assert "Project:" in captured
    assert "Current State:" in captured
    assert "Nodes Created:" in captured
    assert "Trace Lineage:" in captured

    # 2. Test Trace Command
    main(["trace", "--requirement", "REQ-SAR-001"])
    cap_trace = capsys.readouterr().out
    assert "Requirement Trace:" in cap_trace

    # 3. Test Impact Command
    main(["impact", "--component", "500-0771-01"])
    cap_impact = capsys.readouterr().out
    assert "Component Impact:" in cap_impact

    # 4. Test State Command
    main(["state", "--project", "proj_sar_drone_001"])
    cap_state = capsys.readouterr().out
    assert "Current State: VERIFIED" in cap_state

    # 5. Test Timeline Command
    main(["timeline", "--project", "proj_sar_drone_001"])
    cap_time = capsys.readouterr().out
    assert "Project Timeline:" in cap_time
