"""
Unit tests for web source classification and heuristic authority scoring.
"""

from research_agents.web_research_agent.schemas import RawWebResult
from research_agents.web_research_agent.services.authority import AuthorityEvaluator
from research_agents.web_research_agent.services.classification import SourceClassifier


def test_classify_github_repository():
    classifier = SourceClassifier()
    evaluator = AuthorityEvaluator()

    res = RawWebResult(
        title="ultralytics/yolov8",
        url="https://github.com/ultralytics/ultralytics",
    )
    source_type, domain = classifier.classify(res)
    assert source_type == "github_repository"
    assert domain == "github.com"

    auth_score, reasons = evaluator.evaluate_authority(source_type, domain)
    assert auth_score >= 0.90
    assert any("open source" in r.lower() or "repository" in r.lower() for r in reasons)


def test_classify_manufacturer_datasheet():
    classifier = SourceClassifier()
    evaluator = AuthorityEvaluator()

    res = RawWebResult(
        title="TPS54308 4.5V to 28V Input 3A Synchronous Step-Down Converter",
        url="https://www.ti.com/lit/ds/symlink/tps54308.pdf",
    )
    source_type, domain = classifier.classify(res)
    assert source_type == "datasheet"
    assert domain == "ti.com"

    auth_score, reasons = evaluator.evaluate_authority(source_type, domain)
    assert auth_score >= 0.95
    assert any("datasheet" in r.lower() for r in reasons)


def test_classify_forum():
    classifier = SourceClassifier()
    evaluator = AuthorityEvaluator()

    res = RawWebResult(
        title="How to power Jetson Orin Nano from 4S LiPo battery?",
        url="https://forums.raspberrypi.com/viewtopic.php?t=12345",
    )
    source_type, domain = classifier.classify(res)
    assert source_type == "forum"

    auth_score, reasons = evaluator.evaluate_authority(source_type, domain)
    assert auth_score <= 0.50
