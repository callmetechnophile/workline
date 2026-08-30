"""
Unit tests for factual engineering statement extraction and unit normalization.
"""

from research_agents.document_processing_agent.schemas import ExtractedBlock
from research_agents.document_processing_agent.services.fact_extractor import EngineeringFactExtractor
from research_agents.document_processing_agent.services.unit_normalizer import UnitNormalizer


def test_unit_normalization():
    norm = UnitNormalizer()

    val, unit = norm.normalize("500 mA")
    assert val == 0.5
    assert unit == "A"

    val_v, unit_v = norm.normalize("3.3 V")
    assert val_v == 3.3
    assert unit_v == "V"

    val_f, unit_f = norm.normalize("240 MHz")
    assert val_f == 240000000.0
    assert unit_f == "Hz"


def test_fact_extraction_with_provenance():
    extractor = EngineeringFactExtractor()
    blocks = [
        ExtractedBlock(
            block_id="b1",
            page_number=3,
            text="The thermal sensor operates at 3.3 V supply voltage. Peak current draw is 500 mA.",
        )
    ]

    facts = extractor.extract_facts(document_id="paper_101", blocks=blocks)
    assert len(facts) >= 1
    v_fact = next((f for f in facts if f.attribute == "operating_voltage"), None)
    assert v_fact is not None
    assert v_fact.source_document == "paper_101"
    assert v_fact.page == 3
    assert v_fact.normalized_value == 3.3
    assert v_fact.normalized_unit == "V"
