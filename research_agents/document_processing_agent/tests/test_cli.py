"""
Unit tests for DocumentProcessingAgent CLI test runner.
"""

from research_agents.document_processing_agent.__main__ import main


def test_cli_demo_execution(capsys):
    main(["--demo", "--id", "test_demo_doc"])
    captured = capsys.readouterr().out

    assert "Document:" in captured
    assert "Pages:" in captured
    assert "Sections:" in captured
    assert "Quality:" in captured
    assert "Markdown generated" in captured
    assert "Metadata generated" in captured
    assert "Provenance preserved" in captured
