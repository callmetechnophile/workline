"""
Unit tests for cross-source comparison and contradiction detection.
"""

from research_agents.deep_research_agent.schemas import EvidenceItem
from research_agents.deep_research_agent.services.cross_comparator import CrossSourceComparator


def test_cross_source_comparisons_and_contradiction_detection():
    comparator = CrossSourceComparator()
    evidence = [
        EvidenceItem(
            evidence_id="ev_01",
            source_id="datasheet_flir",
            source_type="datasheet",
            text="FLIR Lepton 3.5 operates at 8.7 Hz export frame rate.",
        ),
        EvidenceItem(
            evidence_id="ev_02",
            source_id="paper_ieee",
            source_type="research_paper",
            text="The thermal drone tracking pipeline runs at 30 FPS.",
        ),
        EvidenceItem(
            evidence_id="ev_03",
            source_id="web_nvidia",
            source_type="manufacturer_documentation",
            text="Jetson Orin Nano provides 40 TOPS AI compute at 15 W.",
        ),
        EvidenceItem(
            evidence_id="ev_04",
            source_id="paper_jetson",
            source_type="research_paper",
            text="Jetson Orin Nano benchmarked with YOLOv8 at 15 W power mode.",
        ),
    ]

    comparisons, contradictions = comparator.detect_cross_source_patterns(evidence)

    assert len(comparisons) >= 1
    assert any("Jetson" in c.topic for c in comparisons)

    assert len(contradictions) >= 1
    assert any("Refresh Rate" in ct.topic or "Thermal" in ct.topic for ct in contradictions)
    assert contradictions[0].resolution != ""
