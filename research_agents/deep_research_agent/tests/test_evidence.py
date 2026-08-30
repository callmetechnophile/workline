"""
Unit tests for evidence aggregation, normalization, and validation across Agents #1, #2, #3.
"""

from research_agents.deep_research_agent.schemas import (
    DeepResearchAgentInput,
    ProjectMeta,
)
from research_agents.deep_research_agent.services.evidence_aggregator import EvidenceAggregator


def test_evidence_aggregator_unifies_all_sources():
    aggregator = EvidenceAggregator()
    input_data = DeepResearchAgentInput(
        project=ProjectMeta(title="Autonomous SAR Drone"),
        research_papers=[
            {"paper_id": "paper_101", "title": "Thermal Drone Vision", "abstract": "Achieved 45 FPS on Jetson Orin Nano."}
        ],
        web_sources=[
            {"source_id": "web_ti", "title": "TPS54308 Datasheet", "description": "3A synchronous step-down converter.", "source_type": "datasheet"}
        ],
        documents=[
            {
                "document_id": "doc_proc_01",
                "title": "ESP32 Manual",
                "chunks": [
                    {"chunk_id": "c_1", "text": "Operating at 3.3V supply.", "page_start": 3, "section": "Electrical"}
                ],
            }
        ],
        facts=[
            {"fact": "FLIR Lepton operates at 3.3 V", "source_document": "doc_lepton", "page": 1}
        ],
    )

    evidence, warnings = aggregator.aggregate_and_validate(input_data)

    assert len(evidence) == 4
    ev_ids = [e.evidence_id for e in evidence]
    assert len(set(ev_ids)) == 4  # All distinct IDs

    # Check types
    types = {e.source_type for e in evidence}
    assert "research_paper" in types
    assert "datasheet" in types


def test_evidence_aggregator_flags_empty_sources():
    aggregator = EvidenceAggregator()
    input_data = DeepResearchAgentInput(
        project=ProjectMeta(title="Empty Project"),
        research_papers=[{"title": "Paper Without Text", "abstract": ""}],
    )

    evidence, warnings = aggregator.aggregate_and_validate(input_data)
    assert len(evidence) == 0
    assert len(warnings) >= 1
    assert "no abstract" in warnings[0].lower() or "no text" in warnings[0].lower()
