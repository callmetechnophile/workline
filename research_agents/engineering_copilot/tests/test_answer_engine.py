"""
Unit tests for AnswerEngine evidence grounding and unknown/stale handling (Sections 13, 15, 48–54).
"""

from research_agents.engineering_copilot.schemas import EvidenceObject
from research_agents.engineering_copilot.services.answer_engine import AnswerEngine


def test_answer_engine_grounded_and_edge_cases():
    engine = AnswerEngine()

    # 1. Grounded Requirement Trace
    ans_trace = engine.render_answer(
        intent="REQUIREMENT_TRACE",
        project_id="p1",
        query="Trace REQ-SAR-001",
        evidence=[EvidenceObject(evidence_id="E1", source_type="requirement", source_id="REQ-SAR-001")],
    )
    assert "REQ-SAR-001" in ans_trace
    assert "Traceability Lineage" in ans_trace

    # 2. Unknown Data Handling (Section 49)
    ans_unk = engine.render_answer(
        intent="UNKNOWN",
        project_id="p1",
        query="What is the operating temperature range?",
        evidence=[],
        is_unknown=True,
    )
    assert "UNKNOWN:" in ans_unk
    assert "Missing Evidence" in ans_unk

    # 3. Conflicting Version Handling (Section 50)
    ans_conf = engine.render_answer(
        intent="ARCHITECTURE_QUERY",
        project_id="p1",
        query="What is the system architecture?",
        evidence=[],
        conflict_detected=True,
    )
    assert "CONFLICT_DETECTED:" in ans_conf

    # 4. Stale Architecture Handling (Section 51 & 52)
    ans_stale = engine.render_answer(
        intent="ARCHITECTURE_QUERY",
        project_id="p1",
        query="Show architecture V3 unvalidated draft",
        evidence=[],
        is_stale=True,
    )
    assert "Architecture V2.0.0 is the active validated architecture" in ans_stale
    assert "STALE" in ans_stale
