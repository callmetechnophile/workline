"""Tests for spaCy NLP enrichment, engineering NER, normalizers, and entity resolver."""

import pytest
from backend.workline.documents.docling.parser import DoclingParser
from backend.workline.documents.entities.resolver import EntityResolver, ResolutionStatus
from backend.workline.documents.models import EngineeringEntity, EngineeringEntityType
from backend.workline.documents.spacy.enricher import SpacyEnricher
from backend.workline.documents.spacy.normalizer import EntityNormalizer


def test_engineering_entity_normalization():
    # Voltage normalization
    assert EntityNormalizer.normalize_voltage("3V3") == ("3.3 V", "V")
    assert EntityNormalizer.normalize_voltage("3.3V") == ("3.3 V", "V")
    assert EntityNormalizer.normalize_voltage("12 V") == ("12 V", "V")

    # Current normalization
    assert EntityNormalizer.normalize_current("3A") == ("3 A", "A")
    assert EntityNormalizer.normalize_current("500mA") == ("500 mA", "mA")

    # Temperature normalization
    assert EntityNormalizer.normalize_temperature("125°C") == ("125 °C", "°C")


def test_spacy_ner_extraction():
    content = """# Power Stage Design
The buck regulator TPS62130 delivers up to 3A continuous current with 3V3 regulated output.
Operating temperature is rated up to 125°C.
"""
    doc = DoclingParser.parse("DOC-TEST-1", "rover_v2", content, "power.md")
    entities = SpacyEnricher.enrich(doc)

    assert len(entities) >= 3

    # Check extracted component
    comp_ent = next((e for e in entities if e.entity_type == EngineeringEntityType.COMPONENT), None)
    assert comp_ent is not None
    assert comp_ent.normalized_value == "TPS62130"

    # Check extracted voltage
    volt_ent = next((e for e in entities if e.entity_type == EngineeringEntityType.VOLTAGE), None)
    assert volt_ent is not None
    assert volt_ent.normalized_value == "3.3 V"

    # Check extracted current
    curr_ent = next((e for e in entities if e.entity_type == EngineeringEntityType.CURRENT), None)
    assert curr_ent is not None
    assert curr_ent.normalized_value == "3 A"


def test_entity_resolver_logic():
    ent_a = EngineeringEntity(
        entity_id="e1",
        project_id="p1",
        document_id="d1",
        entity_type=EngineeringEntityType.COMPONENT,
        original_text="TPS62130",
        normalized_value="TPS62130",
    )
    ent_b = EngineeringEntity(
        entity_id="e2",
        project_id="p1",
        document_id="d2",
        entity_type=EngineeringEntityType.COMPONENT,
        original_text="TPS62130RGTR",
        normalized_value="TPS62130RGTR",
    )
    ent_c = EngineeringEntity(
        entity_id="e3",
        project_id="p1",
        document_id="d3",
        entity_type=EngineeringEntityType.COMPONENT,
        original_text="LM2596",
        normalized_value="LM2596",
    )

    # Base vs Suffix alias
    res_alias = EntityResolver.resolve(ent_a, ent_b)
    assert res_alias.status == ResolutionStatus.ALIAS
    assert res_alias.confidence >= 0.8

    # Distinct parts
    res_unresolved = EntityResolver.resolve(ent_a, ent_c)
    assert res_unresolved.status == ResolutionStatus.UNRESOLVED
