"""Tests for Entity Resolution engine, matching strategies, and ambiguous entities."""

import pytest
from backend.workline.knowledge.graph.models import CanonicalEntity, EntityMention, EntityStatus, EntityType
from backend.workline.knowledge.graph.resolver import EntityResolver


@pytest.fixture
def canonical_components():
    return [
        CanonicalEntity(
            entity_id="ENT-TPS62130",
            entity_type=EntityType.COMPONENT,
            canonical_name="TPS62130",
            aliases=["TPS62130RGT"],
            normalized_name="TPS62130",
            project_id="rover_v2",
            manufacturer="Texas Instruments",
            base_part_number="TPS62130",
        ),
        CanonicalEntity(
            entity_id="ENT-LM2596",
            entity_type=EntityType.COMPONENT,
            canonical_name="LM2596",
            aliases=["LM2596S-5.0"],
            normalized_name="LM2596",
            project_id="rover_v2",
            manufacturer="Texas Instruments",
            base_part_number="LM2596",
        ),
    ]


def test_exact_canonical_match(canonical_components):
    mention = EntityMention(
        mention_id="MNT-1",
        document_id="DOC-1",
        entity_type=EntityType.COMPONENT,
        original_text="TPS62130",
        normalized_text="TPS62130",
        source_span="The TPS62130 step-down converter is selected.",
    )
    res = EntityResolver.resolve_mention(mention, canonical_components)
    assert res.status == "RESOLVED"
    assert res.canonical_entity_id == "ENT-TPS62130"
    assert res.confidence == 1.0
    assert res.strategy == "EXACT_CANONICAL_MATCH"


def test_manufacturer_part_match(canonical_components):
    mention = EntityMention(
        mention_id="MNT-2",
        document_id="DOC-2",
        entity_type=EntityType.COMPONENT,
        original_text="TPS62130",
        normalized_text="TPS62130",
        source_span="TI TPS62130 buck regulator.",
    )
    res = EntityResolver.resolve_mention(mention, canonical_components, manufacturer_context="Texas Instruments")
    assert res.status == "RESOLVED"
    assert res.canonical_entity_id == "ENT-TPS62130"
    assert res.confidence >= 0.98


def test_part_number_package_variant(canonical_components):
    mention = EntityMention(
        mention_id="MNT-3",
        document_id="DOC-3",
        entity_type=EntityType.COMPONENT,
        original_text="TPS62130RGTR",
        normalized_text="TPS62130RGTR",
        source_span="Order code TPS62130RGTR taped and reeled.",
    )
    res = EntityResolver.resolve_mention(mention, canonical_components)
    assert res.status == "ALIAS_VARIANT"
    assert res.canonical_entity_id == "ENT-TPS62130"
    assert res.confidence >= 0.85


def test_ambiguous_and_unresolved_entity(canonical_components):
    mention = EntityMention(
        mention_id="MNT-4",
        document_id="DOC-4",
        entity_type=EntityType.COMPONENT,
        original_text="STM32H743ZI",
        normalized_text="STM32H743ZI",
        source_span="STM32H743ZI microcontroller running at 480MHz.",
    )
    res = EntityResolver.resolve_mention(mention, canonical_components)
    assert res.status == "UNRESOLVED"
    assert res.canonical_entity_id is None
    assert res.confidence < 0.5
