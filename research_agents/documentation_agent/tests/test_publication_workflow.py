import pytest
from research_agents.documentation_agent.services.document_engine     import DocumentEngine
from research_agents.documentation_agent.services.publication_workflow import PublicationWorkflow
from research_agents.documentation_agent.providers.mock_provider       import MockDocProvider
from research_agents.documentation_agent.schemas import DocumentType, DocumentStatus, PublicationChannel


def test_full_lifecycle_internal():
    engine    = DocumentEngine(MockDocProvider())
    doc       = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    workflow  = PublicationWorkflow()

    doc, err = workflow.submit_for_review(doc, "alice")
    assert err is None
    assert doc.status == DocumentStatus.IN_REVIEW

    doc, err = workflow.approve(doc, approver="bob")
    assert err is None
    assert doc.status == DocumentStatus.APPROVED

    doc, err = workflow.publish(doc, "bob", PublicationChannel.INTERNAL_REVIEW, armoriq_authorized=False)
    assert err is None
    assert doc.status == DocumentStatus.PUBLISHED


def test_controlled_vault_requires_armoriq():
    engine   = DocumentEngine(MockDocProvider())
    doc      = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    workflow = PublicationWorkflow()
    doc, _   = workflow.submit_for_review(doc, "alice")
    doc, _   = workflow.approve(doc, approver="bob")
    doc, err = workflow.publish(doc, "bob", PublicationChannel.CONTROLLED_VAULT, armoriq_authorized=False)
    assert err is not None
    assert "ARMORIQ_AUTHORIZATION_REQUIRED" in err


def test_external_release_with_armoriq():
    engine   = DocumentEngine(MockDocProvider())
    doc      = engine.create("P1", DocumentType.DESIGN_DESCRIPTION, "DD", "alice", {"Scope": {}})
    workflow = PublicationWorkflow()
    doc, _   = workflow.submit_for_review(doc, "alice")
    doc, _   = workflow.approve(doc, approver="bob")
    doc, err = workflow.publish(doc, "bob", PublicationChannel.EXTERNAL_RELEASE, armoriq_authorized=True)
    assert err is None
    assert doc.status == DocumentStatus.PUBLISHED
