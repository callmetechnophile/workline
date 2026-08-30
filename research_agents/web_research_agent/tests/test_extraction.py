"""
Unit tests for engineering fact extraction and provenance tracking.
"""

from research_agents.web_research_agent.schemas import NormalizedWebSource
from research_agents.web_research_agent.services.extraction import EvidenceExtractor


def test_fact_extraction_with_provenance():
    extractor = EvidenceExtractor()
    source = NormalizedWebSource(
        source_id="src_101",
        title="ESP32-S3 Technical Reference Manual",
        url="https://espressif.com/doc/esp32-s3-manual.pdf",
        domain="espressif.com",
        source_type="official_documentation",
        accessed_at="2026-08-30T06:00:00Z",
        extracted_content="The ESP32-S3 features an Xtensa 32-bit LX7 dual-core processor operating up to 240MHz. Operating voltage is 3.3V supply. Supports Wi-Fi and Bluetooth LE 5.0.",
        source_tool="anakin",
    )

    facts = extractor.extract_facts(source)
    assert len(facts) >= 2
    for fact in facts:
        assert fact.source_id == "src_101"
        assert fact.source_url == "https://espressif.com/doc/esp32-s3-manual.pdf"
        assert fact.extraction_method == "anakin"
        assert fact.confidence > 0.8
        assert fact.retrieved_at == "2026-08-30T06:00:00Z"
        assert fact.category in ("compute", "electrical", "interface", "memory", "software")


def test_github_repository_fact_extraction():
    extractor = EvidenceExtractor()
    source = NormalizedWebSource(
        source_id="src_gh_202",
        title="ros2_uav_thermal_rescue - Autonomous SAR Drone ROS2 Node",
        url="https://github.com/autonomy/ros2_uav_thermal_rescue",
        domain="github.com",
        source_type="github_repository",
        accessed_at="2026-08-30T06:00:00Z",
        description="ROS 2 Humble package for thermal human detection on Jetson Orin Nano with FLIR cameras.",
        source_tool="tavily",
    )

    facts = extractor.extract_facts(source)
    assert len(facts) >= 1
    assert any("Open-source implementation repository" in f.fact for f in facts)
    assert facts[0].source_id == "src_gh_202"
