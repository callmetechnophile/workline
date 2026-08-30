"""
Unit tests for deterministic DOI, title, ID, and URL deduplication.
"""

from research_agents.research_paper_agent.schemas import RawPaperRecord
from research_agents.research_paper_agent.services.deduplication import PaperDeduplicator


def test_deduplicate_by_doi():
    dedup = PaperDeduplicator()
    papers = [
        RawPaperRecord(
            paper_id="p1",
            title="Thermal Detection in UAV Systems",
            doi="10.1109/UAV.2024.001",
        ),
        RawPaperRecord(
            paper_id="p2",
            title="Thermal Detection in UAV Systems (Alt Name)",
            doi="https://doi.org/10.1109/uav.2024.001",
        ),
    ]

    unique = dedup.deduplicate(papers)
    assert len(unique) == 1
    assert unique[0].paper_id == "p1"


def test_deduplicate_by_normalized_title():
    dedup = PaperDeduplicator()
    papers = [
        RawPaperRecord(
            paper_id="p1",
            title="Real-Time Thermal Vision: A Survey!",
        ),
        RawPaperRecord(
            paper_id="p2",
            title="real time thermal vision a survey",
        ),
    ]

    unique = dedup.deduplicate(papers)
    assert len(unique) == 1
    assert unique[0].paper_id == "p1"


def test_deduplicate_by_url():
    dedup = PaperDeduplicator()
    papers = [
        RawPaperRecord(
            paper_id="p1",
            title="First Title",
            paper_url="https://www.example.com/papers/123/",
        ),
        RawPaperRecord(
            paper_id="p2",
            title="Second Title (Different wording)",
            paper_url="http://example.com/papers/123",
        ),
    ]

    unique = dedup.deduplicate(papers)
    assert len(unique) == 1
    assert unique[0].paper_id == "p1"


def test_preserve_distinct_papers():
    dedup = PaperDeduplicator()
    papers = [
        RawPaperRecord(paper_id="p1", title="Thermal Detection Paper A", doi="10.1000/1"),
        RawPaperRecord(paper_id="p2", title="Thermal Detection Paper B", doi="10.1000/2"),
        RawPaperRecord(paper_id="p3", title="Edge Computing in Drone Swarms", doi="10.1000/3"),
    ]

    unique = dedup.deduplicate(papers)
    assert len(unique) == 3
