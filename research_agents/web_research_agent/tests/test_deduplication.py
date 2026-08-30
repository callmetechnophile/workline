"""
Unit tests for URL normalization and web source deduplication.
"""

from research_agents.web_research_agent.schemas import RawWebResult
from research_agents.web_research_agent.services.deduplication import WebSourceDeduplicator


def test_url_normalization_strips_tracking():
    raw_url = "http://www.ti.com/product/TPS54308/?utm_source=google&utm_medium=cpc&ref=xyz#overview"
    normalized = WebSourceDeduplicator.normalize_url(raw_url)
    assert normalized == "https://ti.com/product/TPS54308"


def test_deduplicate_by_canonical_url():
    dedup = WebSourceDeduplicator()
    results = [
        RawWebResult(
            title="NVIDIA Jetson Orin Nano",
            url="https://developer.nvidia.com/embedded/jetson-orin-nano",
            snippet="Documentation page 1",
        ),
        RawWebResult(
            title="NVIDIA Jetson Orin Nano (Duplicate)",
            url="http://www.developer.nvidia.com/embedded/jetson-orin-nano/?utm_source=twitter",
            snippet="Documentation page 2",
        ),
    ]

    unique = dedup.deduplicate(results)
    assert len(unique) == 1
    assert unique[0].url == "https://developer.nvidia.com/embedded/jetson-orin-nano"


def test_deduplicate_by_domain_and_normalized_title():
    dedup = WebSourceDeduplicator()
    results = [
        RawWebResult(
            title="ESP32-S3 Pinout & Hardware Reference!",
            url="https://espressif.com/doc/s3/pinout",
        ),
        RawWebResult(
            title="esp32 s3 pinout hardware reference",
            url="https://espressif.com/doc/s3/pinout-alt",
        ),
    ]

    unique = dedup.deduplicate(results)
    assert len(unique) == 1


def test_deduplicate_by_content_fingerprint():
    dedup = WebSourceDeduplicator()
    content = "The Texas Instruments TPS54308 is a 4.5-V to 28-V input voltage range, 3-A synchronous buck converter with integrated MOSFETs."
    results = [
        RawWebResult(
            title="TPS54308 on Vendor A",
            url="https://vendor-a.com/tps54308",
            content=content,
        ),
        RawWebResult(
            title="Different Title on Vendor B",
            url="https://vendor-b.com/ti-tps54308",
            content=content,
        ),
    ]

    unique = dedup.deduplicate(results)
    assert len(unique) == 1
