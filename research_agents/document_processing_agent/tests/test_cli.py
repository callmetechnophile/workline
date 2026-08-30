"""
Unit tests for DocumentProcessingAgent CLI test runner.
"""

from research_agents.document_processing_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--id", "test_demo_doc"])
    captured = capsys.readouterr().out

    assert "WorkflowGuide AI" in captured
    assert "DocumentProcessingAgent" in captured
    assert "test_demo_doc" in captured
    assert "SUCCESS" in captured
    assert "Document Processing Summary" in captured
    assert "Extracted Semantic Chunks" in captured
