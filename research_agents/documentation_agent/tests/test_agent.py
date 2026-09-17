import pytest
from research_agents.documentation_agent.agent import TechDocAgent


def test_create_document():
    agent  = TechDocAgent()
    result = agent.run({
        "project_id":    "TEST-PROJ",
        "operation":     "create_document",
        "user_id":       "eng.alice",
        "document_type": "FMEA_REPORT",
        "title":         "Thermal FMEA",
    })
    assert result["status"]   == "ok"
    assert result["document"] is not None
    assert result["document"]["status"] == "DRAFT"
    assert result["quality_score"]      is not None


def test_list_documents():
    agent  = TechDocAgent()
    agent.run({"project_id": "PROJ-LIST", "operation": "create_document",
               "user_id": "alice", "document_type": "TEST_PLAN", "title": "Plan A"})
    result = agent.run({"project_id": "PROJ-LIST", "operation": "list_documents"})
    assert result["status"]          == "ok"
    assert len(result["documents"])  >= 1


def test_unknown_operation_returns_error():
    agent  = TechDocAgent()
    result = agent.run({"project_id": "P1", "operation": "do_the_impossible"})
    assert result["status"] == "error"
    assert any("UNKNOWN_OPERATION" in e for e in result["errors"])


def test_get_nonexistent_doc():
    agent  = TechDocAgent()
    result = agent.run({"project_id": "P1", "operation": "get_document", "doc_id": "DOC-NOPE"})
    assert result["status"] == "error"
    assert any("DOCUMENT_NOT_FOUND" in e for e in result["errors"])
