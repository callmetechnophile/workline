import pytest
from research_agents.documentation_agent.agent import TechDocAgent


def test_tenant_isolation_denied():
    agent  = TechDocAgent()
    result = agent.run({
        "project_id":               "PROJ-BAD",
        "operation":                "create_document",
        "unauthorized_project_access": True,
    })
    assert result["status"]  == "access_denied"
    assert any("PROJECT_ACCESS_DENIED" in e for e in result["errors"])


def test_self_approval_denied_via_agent():
    agent  = TechDocAgent()
    # Create + submit for review
    r1 = agent.run({"project_id": "SA-PROJ", "operation": "create_document",
                    "user_id": "alice", "document_type": "DESIGN_DESCRIPTION", "title": "DD"})
    doc_id = r1["document"]["doc_id"]
    agent.run({"project_id": "SA-PROJ", "operation": "review_document",
               "user_id": "alice", "doc_id": doc_id})
    # Alice tries to approve her own document
    r2 = agent.run({"project_id": "SA-PROJ", "operation": "approve_document",
                    "user_id": "alice", "doc_id": doc_id})
    assert r2["status"] == "error"
    assert any("SELF_APPROVAL_DENIED" in e for e in r2["errors"])


def test_controlled_vault_blocked_without_armoriq():
    agent  = TechDocAgent()
    r1 = agent.run({"project_id": "CV-PROJ", "operation": "create_document",
                    "user_id": "alice", "document_type": "DESIGN_DESCRIPTION", "title": "DD"})
    doc_id = r1["document"]["doc_id"]
    agent.run({"project_id": "CV-PROJ", "operation": "review_document",
               "user_id": "alice", "doc_id": doc_id})
    agent.run({"project_id": "CV-PROJ", "operation": "approve_document",
               "user_id": "bob", "doc_id": doc_id})
    r2 = agent.run({
        "project_id": "CV-PROJ", "operation": "publish_document",
        "user_id": "bob", "doc_id": doc_id,
        "metadata": {"channel": "CONTROLLED_VAULT", "armoriq_authorized": False},
    })
    assert r2["status"] == "error"
    assert any("ARMORIQ" in e for e in r2["errors"])
