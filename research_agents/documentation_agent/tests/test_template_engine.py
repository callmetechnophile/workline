import pytest
from research_agents.documentation_agent.services.template_engine import TemplateEngine
from research_agents.documentation_agent.schemas import DocumentType


def test_known_type_returns_sections():
    te = TemplateEngine()
    sections = te.get_sections(DocumentType.SYSTEM_REQUIREMENTS_SPEC.value)
    assert "Scope" in sections
    assert "Functional_Requirements" in sections


def test_unknown_type_returns_default():
    te = TemplateEngine()
    sections = te.get_sections("NONEXISTENT_TYPE")
    assert "Scope" in sections


def test_all_templates_returns_dict():
    te = TemplateEngine()
    tmpl = te.all_templates()
    assert isinstance(tmpl, dict)
    assert DocumentType.FMEA_REPORT.value in tmpl
